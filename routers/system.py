import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from config import VARIABLES

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/system", response_class=HTMLResponse)
async def exploitation_page(request: Request):
    return templates.TemplateResponse("system.html", {"request": request})

@router.get("/api/system/infos")
async def get_infos_data():
    try:
        from main import get_opcua_client
        opcua = get_opcua_client()
        
        ntp_sync = await opcua.read_variable(VARIABLES["ntp_sync"])
        sys_version = await opcua.read_variable(VARIABLES["sys_version"])
        sys_name = await opcua.read_variable(VARIABLES["sys_name"])
        sw_version = await opcua.read_variable(VARIABLES["sw_version"])
        
        html = f"""
        <div class="data-row">
            <span class="label">NTP SYNC</span>
            <span class="value">{ntp_sync}</span>
        </div>
        <div class="data-row">
            <span class="label">SYS VERSION</span>
            <span class="value">{sys_version}</span>
        </div>
        <div class="data-row">
            <span class="label">SYS NAME</span>
            <span class="value">{sys_name}</span>
        </div>
        <div class="data-row">
            <span class="label">SW</span>
            <span class="value">{sw_version}</span>
        </div>
        """
        
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f'<div class="data-row"><span class="label">Error: {str(e)}</span></div>')