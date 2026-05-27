package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/go-redis/redis/v8"
)

// ============================================================================
// 1. LEGACY STRUCTS & LOGIC (Backward Compatibility for CLI bridge)
// ============================================================================

type Agent struct {
	ID   string `json:"id"`
	Role string `json:"role"`
}

type Proposal struct {
	AgentID   string  `json:"agent_id"`
	Solution  string  `json:"solution"`
	RiskScore float64 `json:"risk_score"` // 0.0 (Safe) to 1.0 (Critical)
}

type Decision struct {
	ApprovedProposal Proposal `json:"approved_proposal"`
	ConsensusReached bool     `json:"consensus_reached"`
	SystemMetrics    string   `json:"system_metrics"`
}

type CouncilOfSages struct {
	ThresholdRisk float64
}

func (c *CouncilOfSages) Evaluate(proposals []Proposal) (Decision, error) {
	if len(proposals) == 0 {
		return Decision{}, fmt.Errorf("no proposals submitted for evaluation")
	}

	var bestProposal Proposal
	found := false
	minRisk := 1.0

	for _, prop := range proposals {
		if prop.RiskScore <= c.ThresholdRisk && prop.RiskScore < minRisk {
			minRisk = prop.RiskScore
			bestProposal = prop
			found = true
		}
	}

	if !found {
		return Decision{
			ConsensusReached: false,
			SystemMetrics:    "All proposals rejected due to high security risk profiles.",
		}, nil
	}

	return Decision{
		ApprovedProposal: bestProposal,
		ConsensusReached: true,
		SystemMetrics:    fmt.Sprintf("Consensus reached on Agent [%s] proposal. Risk level: %.2f", bestProposal.AgentID, bestProposal.RiskScore),
	}, nil
}

func ExecuteTask(ctx context.Context, agents []Agent, task string, council *CouncilOfSages) (Decision, error) {
	proposalChan := make(chan Proposal, len(agents))
	var wg sync.WaitGroup

	for _, agent := range agents {
		wg.Add(1)
		go func(a Agent) {
			defer wg.Done()
			select {
			case <-time.After(100 * time.Millisecond):
				risk := 0.1
				if a.ID == "Agent-Security-QA" {
					risk = 0.05
				} else if a.ID == "Agent-Rapid-Dev" {
					risk = 0.45
				}
				proposalChan <- Proposal{
					AgentID:   a.ID,
					Solution:  fmt.Sprintf("[%s] processed task: '%s' with custom optimization matrix.", a.Role, task),
					RiskScore: risk,
				}
			case <-ctx.Done():
				return
			}
		}(agent)
	}

	wg.Wait()
	close(proposalChan)

	var proposals []Proposal
	for prop := range proposalChan {
		proposals = append(proposals, prop)
	}

	return council.Evaluate(proposals)
}

func runLegacyCLI(task string, threshold float64) {
	agents := []Agent{
		{ID: "Agent-Arch", Role: "Software Architect"},
		{ID: "Agent-Rapid-Dev", Role: "Rapid Developer"},
		{ID: "Agent-Security-QA", Role: "Security & QA Auditor"},
	}

	council := &CouncilOfSages{ThresholdRisk: threshold}
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	decision, err := ExecuteTask(ctx, agents, task, council)
	if err != nil {
		errMap := map[string]string{"error": err.Error()}
		errJSON, _ := json.Marshal(errMap)
		fmt.Println(string(errJSON))
		return
	}

	output, err := json.MarshalIndent(decision, "", "  ")
	if err != nil {
		errMap := map[string]string{"error": fmt.Sprintf("Error marshaling JSON: %v", err)}
		errJSON, _ := json.Marshal(errMap)
		fmt.Println(string(errJSON))
		return
	}
	fmt.Println(string(output))
}

// ============================================================================
// 2. LIVE REST/JSON SERVER STRUCTS & LOGIC
// ============================================================================

type ProposalRequest struct {
	AgentID        string  `json:"agent_id"`
	Role           string  `json:"role"`
	TaskId         string  `json:"task_id"`
	CodePayload    string  `json:"code_payload"`
	RiskAssessment float64 `json:"risk_assessment"`
}

type ProposalResponse struct {
	ProposalID    string `json:"proposal_id"`
	Received      bool   `json:"received"`
	StatusMessage string `json:"status_message"`
}

type ConsensusRequest struct {
	TaskId           string            `json:"task_id"`
	Proposals        []ProposalRequest `json:"proposals"`
	MaxRiskThreshold float64           `json:"max_risk_threshold"`
}

type ConsensusResponse struct {
	TaskId           string  `json:"task_id"`
	ApprovedAgentID  string  `json:"approved_agent_id"`
	ApprovedPayload  string  `json:"approved_payload"`
	EvaluatedRisk    float64 `json:"evaluated_risk"`
	ConsensusReached bool    `json:"consensus_reached"`
	AuditLogs        string  `json:"audit_logs"`
}

type Server struct {
	rdb        *redis.Client
	localCache sync.Map // sync.Map fallback memory state if Redis is offline
	useLocal   bool
}

func NewServer(redisAddr string) *Server {
	rdb := redis.NewClient(&redis.Options{
		Addr:         redisAddr,
		DialTimeout:  500 * time.Millisecond,
		ReadTimeout:  500 * time.Millisecond,
		WriteTimeout: 500 * time.Millisecond,
	})

	// Check if Redis is alive
	ctx, cancel := context.WithTimeout(context.Background(), 800*time.Millisecond)
	defer cancel()

	useLocal := false
	if err := rdb.Ping(ctx).Err(); err != nil {
		log.Printf("⚠️ Redis server not responding at %s. Falling back to local in-memory thread-safe state.", redisAddr)
		useLocal = true
	} else {
		log.Printf("🔌 Connected to Redis sovereign memory cluster at %s", redisAddr)
	}

	return &Server{
		rdb:      rdb,
		useLocal: useLocal,
	}
}

// REST Handlers

func (s *Server) handleSubmitProposal(w http.ResponseWriter, r *http.Header, body []byte) ([]byte, int) {
	var req ProposalRequest
	if err := json.Unmarshal(body, &req); err != nil {
		return []byte(fmt.Sprintf(`{"error": "Invalid JSON body: %v"}`, err)), http.StatusBadRequest
	}

	if req.AgentID == "" || req.TaskId == "" {
		return []byte(`{"error": "Missing agent_id or task_id"}`), http.StatusBadRequest
	}

	key := fmt.Sprintf("task:%s:proposal:%s", req.TaskId, req.AgentID)

	if s.useLocal {
		// Cache in sync.Map
		s.localCache.Store(key, req)
	} else {
		// Cache in Redis
		ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
		defer cancel()

		reqData, _ := json.Marshal(req)
		err := s.rdb.Set(ctx, key, reqData, 1*time.Hour).Err()
		if err != nil {
			// Failover to local cache
			log.Printf("⚠️ Redis write error, falling back to local memory: %v", err)
			s.localCache.Store(key, req)
		}
	}

	res := ProposalResponse{
		ProposalID:    key,
		Received:      true,
		StatusMessage: "Proposal cached successfully in sovereign memory.",
	}
	resBytes, _ := json.Marshal(res)
	return resBytes, http.StatusOK
}

func (s *Server) handleEvaluateConsensus(w http.ResponseWriter, r *http.Header, body []byte) ([]byte, int) {
	var req ConsensusRequest
	if err := json.Unmarshal(body, &req); err != nil {
		return []byte(fmt.Sprintf(`{"error": "Invalid JSON body: %v"}`, err)), http.StatusBadRequest
	}

	if req.TaskId == "" {
		return []byte(`{"error": "Missing task_id"}`), http.StatusBadRequest
	}

	if len(req.Proposals) == 0 {
		return []byte(`{"error": "No proposals provided for evaluation"}`), http.StatusBadRequest
	}

	var bestProposal *ProposalRequest
	minRisk := 1.0
	consensusReached := false
	var auditLogs string

	for i, prop := range req.Proposals {
		auditLogs += fmt.Sprintf("[%d] Evaluating Agent [%s] (%s): Risk = %.2f\n", i+1, prop.AgentID, prop.Role, prop.RiskAssessment)

		if prop.RiskAssessment <= req.MaxRiskThreshold && prop.RiskAssessment < minRisk {
			minRisk = prop.RiskAssessment
			bestProposal = &req.Proposals[i]
			consensusReached = true
		}
	}

	var res ConsensusResponse
	res.TaskId = req.TaskId

	if !consensusReached {
		auditLogs += "Decision: Consensus FAILED. All proposals exceed safety threshold."
		res.ConsensusReached = false
		res.EvaluatedRisk = 1.0
		res.AuditLogs = auditLogs
	} else {
		auditLogs += fmt.Sprintf("Decision: Consensus REACHED. Selected Agent [%s] with Risk = %.2f", bestProposal.AgentID, bestProposal.RiskAssessment)
		res.ConsensusReached = true
		res.ApprovedAgentID = bestProposal.AgentID
		res.ApprovedPayload = bestProposal.CodePayload
		res.EvaluatedRisk = bestProposal.RiskAssessment
		res.AuditLogs = auditLogs

		// Archive consensus decision
		archiveKey := fmt.Sprintf("task:%s:consensus", req.TaskId)
		if s.useLocal {
			s.localCache.Store(archiveKey, res)
		} else {
			ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
			defer cancel()

			resData, _ := json.Marshal(res)
			_ = s.rdb.Set(ctx, archiveKey, resData, 24*time.Hour).Err()
		}
	}

	resBytes, _ := json.Marshal(res)
	return resBytes, http.StatusOK
}

// REST router / handler wrapper
func (s *Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
	w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	if r.URL.Path == "/status" {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(fmt.Sprintf(`{"status": "active", "redis_online": %t}`, !s.useLocal)))
		return
	}

	if r.Method != "POST" {
		w.WriteHeader(http.StatusMethodNotAllowed)
		w.Write([]byte(`{"error": "Only POST requests are allowed"}`))
		return
	}

	// Read body
	var body []byte
	if r.Body != nil {
		defer r.Body.Close()
		var err error
		body, err = ioReadFull(r.Body)
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{"error": "Failed to read request body"}`))
			return
		}
	}

	var resBytes []byte
	var status int

	switch r.URL.Path {
	case "/submit_proposal":
		resBytes, status = s.handleSubmitProposal(w, &r.Header, body)
	case "/evaluate_consensus":
		resBytes, status = s.handleEvaluateConsensus(w, &r.Header, body)
	case "/status":
		status = http.StatusOK
		resBytes = []byte(fmt.Sprintf(`{"status": "active", "redis_online": %t}`, !s.useLocal))
	default:
		status = http.StatusNotFound
		resBytes = []byte(`{"error": "Endpoint not found"}`)
	}

	w.WriteHeader(status)
	w.Write(resBytes)
}

// Helper to avoid io package import for simplicity
func ioReadFull(r ioReader) ([]byte, error) {
	var result []byte
	buf := make([]byte, 1024)
	for {
		n, err := r.Read(buf)
		if n > 0 {
			result = append(result, buf[:n]...)
		}
		if err != nil {
			if err.Error() == "EOF" {
				return result, nil
			}
			return nil, err
		}
	}
}

type ioReader interface {
	Read(p []byte) (n int, err error)
}

// ============================================================================
// 3. MAIN RUNNER
// ============================================================================

func main() {
	// CLI Flags (Checks CLI and Legacy backward compatibility)
	taskPtr := flag.String("task", "", "Direct CLI task evaluation (legacy/backward compatibility)")
	thresholdPtr := flag.Float64("threshold", 0.3, "The risk threshold for legacy CLI execution")
	
	// REST Flags
	serverModePtr := flag.Bool("server", false, "Start the high-performance REST/JSON server")
	portPtr := flag.String("port", "50051", "Port to start the REST/JSON server on")
	redisPtr := flag.String("redis", "localhost:6379", "Redis server address")
	
	flag.Parse()

	// If no flags are provided, but we aren't executing CLI, default to server mode if triggered from bridge
	if *taskPtr != "" {
		// Run in legacy CLI mode
		runLegacyCLI(*taskPtr, *thresholdPtr)
		return
	}

	// Default to server mode if explicitly flag-set or if CLI mode is blank
	if *serverModePtr || *taskPtr == "" {
		// Parse environment overrides
		port := *portPtr
		if envPort := os.Getenv("GO_COORDINATOR_PORT"); envPort != "" {
			port = envPort
		}
		redisAddr := *redisPtr
		if envRedis := os.Getenv("REDIS_ADDR"); envRedis != "" {
			redisAddr = envRedis
		}

		// Initialize & Start Server
		server := NewServer(redisAddr)
		
		addr := ":" + port
		listener, err := net.Listen("tcp", addr)
		if err != nil {
			log.Fatalf("❌ Failed to bind to port %s: %v", port, err)
		}
		
		log.Printf("⚡ Nexum-Core Sovereign Go Coordinator REST server active on port %s", port)
		if err := http.Serve(listener, server); err != nil {
			log.Fatalf("❌ Server error: %v", err)
		}
	}
}
