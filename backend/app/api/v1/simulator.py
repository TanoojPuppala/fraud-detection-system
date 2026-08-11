"""
Transaction Simulator Control Endpoints (/api/v1/simulator).
"""

from fastapi import APIRouter
from backend.app.services.simulator_service import simulator_service
from backend.app.schemas.analytics import SimulatorControl, SimulatorStatus

router = APIRouter(prefix="/simulator", tags=["Real-time Simulator"])


@router.post("/start", response_model=SimulatorStatus)
def start_simulator(control: SimulatorControl):
    interval = control.interval_seconds if control.interval_seconds else 2.0
    simulator_service.start(interval_seconds=interval)
    return simulator_service.get_status()


@router.post("/stop", response_model=SimulatorStatus)
def stop_simulator():
    simulator_service.stop()
    return simulator_service.get_status()


@router.get("/status", response_model=SimulatorStatus)
def get_simulator_status():
    return simulator_service.get_status()
