from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from config import VARIABLES

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/communication", response_class=HTMLResponse)
async def communication_page(request: Request):
    return templates.TemplateResponse("communication.html", {"request": request})

@router.get("/api/communication")
async def get_communication():
    try:
        from main import get_opcua_client
        opcua_client = get_opcua_client()
        
        comm_vars = {
            "RIO": await opcua_client.read_variable(VARIABLES["rio_comflt"]),
            "BESS": await opcua_client.read_variable(VARIABLES["bess_comflt"]), 
            "JBOX": await opcua_client.read_variable(VARIABLES["jbox"]),
            "HMI Service - PDC1/2": await opcua_client.read_variable(VARIABLES["hmi_service_12"]),
            "CS Service - PDC1/2": await opcua_client.read_variable(VARIABLES["cs_service_12"]),
            "HMI Service - PDC3/4": await opcua_client.read_variable(VARIABLES["hmi_service_34"]),
            "CS Service - PDC3/4": await opcua_client.read_variable(VARIABLES["cs_service_34"]),
            "EVI - PDC1": await opcua_client.read_variable(VARIABLES["evi_p1_comok"]),
            "EVI - PDC2": await opcua_client.read_variable(VARIABLES["evi_p2_comok"]),
            "EVI - PDC3": await opcua_client.read_variable(VARIABLES["evi_p3_comok"]),
            "EVI - PDC4": await opcua_client.read_variable(VARIABLES["evi_p4_comok"]),
            "DCBM 1": await opcua_client.read_variable(VARIABLES["dcbm1_comflt"]),
            "DCBM 2": await opcua_client.read_variable(VARIABLES["dcbm2_comflt"]),
            "DCBM 3": await opcua_client.read_variable(VARIABLES["dcbm3_comflt"]),
            "DCBM 4": await opcua_client.read_variable(VARIABLES["dcbm4_comflt"]),
        }
        
        inverted_logic = ["EVI - PDC1", "EVI - PDC2", "EVI - PDC3", "EVI - PDC4"]
        
        html = ""
        for label, value in comm_vars.items():
            if label in inverted_logic:
                status_class = "success" if value else "danger"
            else:
                status_class = "danger" if value else "success"
            
            html += f"""
            <div class="comm-item">
                <span class="comm-label">{label}</span>
                <span class="indicator {status_class}"></span>
            </div>
            """
        
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f'<div class="comm-item"><span class="comm-label">Error: {str(e)}</span></div>')

@router.get("/api/communication/modules")
async def get_modules_status():
    try:
        from main import get_opcua_client
        opcua_client = get_opcua_client()
        
        modules = {}
        for i in range(1, 15):
            value = await opcua_client.read_variable(VARIABLES[f"mxrx_{i}_com"])
            modules[f"M{i}"] = {
                "fault": bool(value),
                "color": "#22c55e" if value else "#ef4444"
            }
        
        return {"modules": modules}
        
    except Exception as e:
        return {"error": str(e)}