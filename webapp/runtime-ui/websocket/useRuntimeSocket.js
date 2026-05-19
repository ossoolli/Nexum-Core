import { useEffect } from 'react';
import { useRuntimeStore } from '../stores/useRuntimeStore';

const WEBSOCKET_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:5000/ws';

export function useRuntimeSocket() {
  const { setAgents, addLog, updateMetrics } = useRuntimeStore();

  useEffect(() => {
    const ws = new WebSocket(WEBSOCKET_URL);

    ws.onopen = () => {
      console.log('🔗 Connected to Sovereign Runtime');
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'init') {
        setAgents(msg.agents);
      } else if (msg.type === 'event') {
        addLog(msg.event);
      } else if (msg.type === 'metrics') {
        updateMetrics(msg.data);
      }
    };

    ws.onclose = () => {
      console.log('⚠️ Lost connection to Sovereign Runtime. Reconnecting...');
      // Implement fallback / retry
    };

    return () => ws.close();
  }, [setAgents, addLog, updateMetrics]);
}
