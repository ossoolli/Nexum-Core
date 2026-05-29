import asyncio
from core.learning.evolution_engine import SovereignEvolutionEngine
from council.consensus_engine import council_consensus

async def main():
    engine = SovereignEvolutionEngine(council=council_consensus)
    print("Running diagnostic and evolution loop...")
    report = engine.run_diagnostics_and_evolve(admin_id=1) # Replace with a real admin ID if needed
    print(f"Evolution Report: {report}")

if __name__ == "__main__":
    asyncio.run(main())
