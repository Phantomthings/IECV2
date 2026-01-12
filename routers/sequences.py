import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from config import VARIABLES

router = APIRouter()
templates = Jinja2Templates(directory="templates")


FAST_PULSE_COMMANDS = {
    "ack",
    "es",
}

@router.get("/sequences", response_class=HTMLResponse)
async def sequences_page(request: Request):
    return templates.TemplateResponse("sequences.html", {"request": request})

@router.get("/api/sequences/pdc1")
async def get_pdc1_data():
    try:
        from main import get_opcua_client
        opcua = get_opcua_client()
        
        seq12_ready = await opcua.read_variable(VARIABLES["seq12_ready"])
        seq12_fault = await opcua.read_variable(VARIABLES["seq12_fault"])
        seq12_ic = await opcua.read_variable(VARIABLES["seq12_ic"])
        seq12_pc = await opcua.read_variable(VARIABLES["seq12_pc"])
        seq12_branch = await opcua.read_variable(VARIABLES["seq12_branch"])
        seq12_ack_val = await opcua.read_variable(VARIABLES["seq12_ack"])
        seq12_hmi = await opcua.read_variable(VARIABLES["seq12_hmi"])

        hc1p1_current = await opcua.read_variable(VARIABLES["hc1p1_current"])
        hc1p1_voltage = await opcua.read_variable(VARIABLES["hc1p1_voltage"])
        pdc1_plim = await opcua.read_variable(VARIABLES["pdc1_plim"])
        
        evi1_cp_status = await opcua.read_variable(VARIABLES["evi1_cp_status"])
        evi1_substatus = await opcua.read_variable(VARIABLES["evi1_substatus"])
        evi1_error = await opcua.read_variable(VARIABLES["evi1_error"])
        evi1_pilot = await opcua.read_variable(VARIABLES["evi1_pilot"])
        evi1_voltage = await opcua.read_variable(VARIABLES["evi1_voltage"])
        evi1_target_current = await opcua.read_variable(VARIABLES["evi1_target_current"])
        evi1_target_voltage = await opcua.read_variable(VARIABLES["evi1_target_voltage"])
        evi1_soc = await opcua.read_variable(VARIABLES["evi1_soc"])
        
        evi1_temp1 = await opcua.read_variable(VARIABLES["evi1_temp1"])
        evi1_temp2 = await opcua.read_variable(VARIABLES["evi1_temp2"])
        dcbm1_temp_h = await opcua.read_variable(VARIABLES["dcbm1_temp_h"])
        dcbm1_temp_l = await opcua.read_variable(VARIABLES["dcbm1_temp_l"])
        
        seq12_ready_class = "success" if seq12_ready else "danger"
        seq12_fault_class = "danger" if seq12_fault else "inactive"
        seq12_ack_class = "cmd-btn"
        
        evi1_ack_class = "cmd-btn"
        evi1_es_class = "cmd-btn"

        ic_translations = decode_bits(seq12_ic, IC_MAP)
        pc_translations = decode_bits(seq12_pc, PC_MAP)
        
        hmi_state = decode_hmi (seq12_hmi)
        cpstatusCode = decode_CPStatusCode (evi1_cp_status)
        pilotstatusCode = decode_PilotStatus (evi1_pilot)
        ic_html = "<br>".join(ic_translations)
        pc_html = "<br>".join(pc_translations)

        html = f"""
        <div class="seq-section">
            <h4>Sequence 12</h4>
            <div class="data-row">
                <span class="label">Ready</span>
                <span class="indicator {seq12_ready_class}"></span>
            </div>
            <div class="data-row">
                <span class="label">Fault</span>
                <span class="indicator {seq12_fault_class}"></span>
            </div>
            <div class="data-row">
                <span class="label">IC</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{seq12_ic}</span>
                    <div style="font-size: 0.62rem; color: var(--text-secondary); text-align: left;">
                        {ic_html}
                    </div>
                </div>
            </div>

            <div class="data-row">
                <span class="label">PC</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{seq12_pc}</span>
                    <div style="font-size: 0.62rem; color: var(--text-secondary); text-align: left;">
                        {pc_html}
                    </div>
                </div>
            </div>
            <div class="data-row">
                <span class="label">Step</span>
                <span class="value">{seq12_branch}</span>
            </div>
            <div class="data-row">
                <span class="label">HMI</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{seq12_hmi}</span>
                    <span style="font-size: 0.62rem; color: var(--text-secondary);">{hmi_state}</span>
                </div>
            </div>
            <div class="cmd-row">
                <button class="{seq12_ack_class}" hx-post="/api/sequences/seq12/ack" hx-swap="none">Séquence 12 - Ack</button>
            </div>
        </div>
        
        <div class="seq-section">
            <h4>HC1P1</h4>
            <div class="data-row">
                <span class="label">Current Measurement</span>
                <span class="value">{hc1p1_current:.2f} A</span>
            </div>
            <div class="data-row">
                <span class="label">Voltage Measurement</span>
                <span class="value">{hc1p1_voltage:.2f} V</span>
            </div>
            <div class="data-row">
                <span class="label">Power limitation</span>
                <span class="value">{pdc1_plim:.2f} Kw</span>
            </div>
        </div>
        
        <div class="seq-section">
            <h4>EVI1</h4>
            <div class="data-row">
                <span class="label">CP Status Code</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{evi1_cp_status}</span>
                    <span style="font-size: 0.62rem; color: var(--text-secondary);">{cpstatusCode}</span>
                </div>
            </div>
            <div class="data-row">
                <span class="label">Substate</span>
                <span class="value">{evi1_substatus}</span>
            </div>
            <div class="data-row">
                <span class="label">Error Code</span>
                <span class="value">{evi1_error}</span>
            </div>
            <div class="data-row">
                <span class="label">Pilot Status Code</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{evi1_pilot}</span>
                    <span style="font-size: 0.62rem; color: var(--text-secondary);">{pilotstatusCode}</span>
                </div>
            </div>
            <div class="data-row">
                <span class="label">EVI Voltage Measurement</span>
                <span class="value">{evi1_voltage} V</span>
            </div>
            <div class="data-row">
                <span class="label">Target Current</span>
                <span class="value">{evi1_target_current} A</span>
            </div>
            <div class="data-row">
                <span class="label">Target Voltage</span>
                <span class="value">{evi1_target_voltage} V</span>
            </div>
            <div class="data-row">
                <span class="label">SOC</span>
                <span class="value">{evi1_soc} %</span>
            </div>
            <div class="cmd-row">
                <button class="{evi1_ack_class}" hx-post="/api/sequences/evi1/ack" hx-swap="none">EVI - Ack</button>
                <button class="{evi1_es_class}" hx-post="/api/sequences/evi1/es" hx-swap="none">EVI - ES</button>
            </div>
        </div>
        
        <div class="seq-section">
            <h4>Temperature</h4>
            <div class="data-row">
                <span class="label">Temperature pistolet 1</span>
                <span class="value">{evi1_temp1} °C</span>
            </div>
            <div class="data-row">
                <span class="label">Temperature pistolet 2</span>
                <span class="value">{evi1_temp2} °C</span>
            </div>
            <div class="data-row">
                <span class="label">Temperature DCBM_H</span>
                <span class="value">{dcbm1_temp_h} °C</span>
            </div>
            <div class="data-row">
                <span class="label">Temperature DCBM_L</span>
                <span class="value">{dcbm1_temp_l} °C</span>
            </div>
        </div>
        """
        
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f'<div class="seq-section"><span class="label">Error: {str(e)}</span></div>')

@router.get("/api/sequences/pdc2")
async def get_pdc2_data():
    try:
        from main import get_opcua_client
        opcua = get_opcua_client()
        
        seq22_ready = await opcua.read_variable(VARIABLES["seq22_ready"])
        seq22_fault = await opcua.read_variable(VARIABLES["seq22_fault"])
        seq22_ic = await opcua.read_variable(VARIABLES["seq22_ic"])
        seq22_pc = await opcua.read_variable(VARIABLES["seq22_pc"])
        seq22_branch = await opcua.read_variable(VARIABLES["seq22_branch"])
        seq22_ack_val = await opcua.read_variable(VARIABLES["seq22_ack"])
        seq22_hmi = await opcua.read_variable(VARIABLES["seq22_hmi"])

        hc1p2_current = await opcua.read_variable(VARIABLES["hc1p2_current"])
        hc1p2_voltage = await opcua.read_variable(VARIABLES["hc1p2_voltage"])
        pdc2_plim = await opcua.read_variable(VARIABLES["pdc2_plim"])
        
        evi2_cp_status = await opcua.read_variable(VARIABLES["evi2_cp_status"])
        evi2_substatus = await opcua.read_variable(VARIABLES["evi2_substatus"])
        evi2_error = await opcua.read_variable(VARIABLES["evi2_error"])
        evi2_pilot = await opcua.read_variable(VARIABLES["evi2_pilot"])
        evi2_voltage = await opcua.read_variable(VARIABLES["evi2_voltage"])
        evi2_target_current = await opcua.read_variable(VARIABLES["evi2_target_current"])
        evi2_target_voltage = await opcua.read_variable(VARIABLES["evi2_target_voltage"])
        evi2_soc = await opcua.read_variable(VARIABLES["evi2_soc"])
        
        evi2_temp1 = await opcua.read_variable(VARIABLES["evi2_temp1"])
        evi2_temp2 = await opcua.read_variable(VARIABLES["evi2_temp2"])
        dcbm2_temp_h = await opcua.read_variable(VARIABLES["dcbm2_temp_h"])
        dcbm2_temp_l = await opcua.read_variable(VARIABLES["dcbm2_temp_l"])
        
        seq22_ready_class = "success" if seq22_ready else "danger"
        seq22_fault_class = "danger" if seq22_fault else "inactive"
        seq22_ack_class = "cmd-btn"
        
        evi2_ack_class = "cmd-btn"
        evi2_es_class = "cmd-btn"
        
        ic_translations = decode_bits(seq22_ic, IC_MAP)
        pc_translations = decode_bits(seq22_pc, PC_MAP)
        
        hmi_state = decode_hmi (seq22_hmi)
        cpstatusCode = decode_CPStatusCode (evi2_cp_status)
        pilotstatusCode = decode_PilotStatus (evi2_pilot)
        ic_html = "<br>".join(ic_translations)
        pc_html = "<br>".join(pc_translations)

        html = f"""
        <div class="seq-section">
            <h4>Sequence 22</h4>
            <div class="data-row">
                <span class="label">Ready</span>
                <span class="indicator {seq22_ready_class}"></span>
            </div>
            <div class="data-row">
                <span class="label">Fault</span>
                <span class="indicator {seq22_fault_class}"></span>
            </div>
            <div class="data-row">
                <span class="label">IC</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{seq22_ic}</span>
                    <div style="font-size: 0.62rem; color: var(--text-secondary); text-align: left;">
                        {ic_html}
                    </div>
                </div>
            </div>

            <div class="data-row">
                <span class="label">PC</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{seq22_pc}</span>
                    <div style="font-size: 0.62rem; color: var(--text-secondary); text-align: left;">
                        {pc_html}
                    </div>
                </div>
            </div>
            <div class="data-row">
                <span class="label">Step</span>
                <span class="value">{seq22_branch}</span>
            </div>
            <div class="data-row">
                <span class="label">HMI</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{seq22_hmi}</span>
                    <span style="font-size: 0.62rem; color: var(--text-secondary);">{hmi_state}</span>
                </div>
            </div>
            <div class="cmd-row">
                <button class="{seq22_ack_class}" hx-post="/api/sequences/seq12/ack" hx-swap="none">Séquence 22 - Ack</button>
            </div>
        </div>
        
        <div class="seq-section">
            <h4>HC1P2</h4>
            <div class="data-row">
                <span class="label">Current Measurement</span>
                <span class="value">{hc1p2_current:.2f} A</span>
            </div>
            <div class="data-row">
                <span class="label">Voltage Measurement</span>
                <span class="value">{hc1p2_voltage:.2f} V</span>
            </div>
            <div class="data-row">
                <span class="label">Power limitation</span>
                <span class="value">{pdc2_plim:.2f} Kw</span>
            </div>
        </div>
        
        <div class="seq-section">
            <h4>EVI2</h4>
            <div class="data-row">
                <span class="label">CP Status Code</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{evi2_cp_status}</span>
                    <span style="font-size: 0.62rem; color: var(--text-secondary);">{cpstatusCode}</span>
                </div>
            </div>
            <div class="data-row">
                <span class="label">Substate</span>
                <span class="value">{evi2_substatus}</span>
            </div>
            <div class="data-row">
                <span class="label">Error Code</span>
                <span class="value">{evi2_error}</span>
            </div>
            <div class="data-row">
                <span class="label">Pilot Status Code</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{evi2_pilot}</span>
                    <span style="font-size: 0.62rem; color: var(--text-secondary);">{pilotstatusCode}</span>
                </div>
            </div>
            <div class="data-row">
                <span class="label">EVI Voltage Measurement</span>
                <span class="value">{evi2_voltage} V</span>
            </div>
            <div class="data-row">
                <span class="label">Target Current</span>
                <span class="value">{evi2_target_current} A</span>
            </div>
            <div class="data-row">
                <span class="label">Target Voltage</span>
                <span class="value">{evi2_target_voltage} V</span>
            </div>
            <div class="data-row">
                <span class="label">SOC</span>
                <span class="value">{evi2_soc} %</span>
            </div>
            <div class="cmd-row">
                <button class="{evi2_ack_class}" hx-post="/api/sequences/evi2/ack" hx-swap="none">EVI - Ack</button>
                <button class="{evi2_es_class}" hx-post="/api/sequences/evi2/es" hx-swap="none">EVI - ES</button>
            </div>
        </div>
        
        <div class="seq-section">
            <h4>Temperature</h4>
            <div class="data-row">
                <span class="label">Temperature pistolet 1</span>
                <span class="value">{evi2_temp1} °C</span>
            </div>
            <div class="data-row">
                <span class="label">Temperature pistolet 2</span>
                <span class="value">{evi2_temp2} °C</span>
            </div>
            <div class="data-row">
                <span class="label">Temperature DCBM_H</span>
                <span class="value">{dcbm2_temp_h} °C</span>
            </div>
            <div class="data-row">
                <span class="label">Temperature DCBM_L</span>
                <span class="value">{dcbm2_temp_l} °C</span>
            </div>
        </div>
        """
        
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f'<div class="seq-section"><span class="label">Error: {str(e)}</span></div>')

@router.get("/api/sequences/pdc3")
async def get_pdc3_data():
    try:
        from main import get_opcua_client
        opcua = get_opcua_client()
        
        seq13_ready = await opcua.read_variable(VARIABLES["seq13_ready"])
        seq13_fault = await opcua.read_variable(VARIABLES["seq13_fault"])
        seq13_ic = await opcua.read_variable(VARIABLES["seq13_ic"])
        seq13_pc = await opcua.read_variable(VARIABLES["seq13_pc"])
        seq13_branch = await opcua.read_variable(VARIABLES["seq13_branch"])
        seq13_ack_val = await opcua.read_variable(VARIABLES["seq13_ack"])
        seq13_hmi = await opcua.read_variable(VARIABLES["seq13_hmi"])

        hc2p3_current = await opcua.read_variable(VARIABLES["hc2p3_current"])
        hc2p3_voltage = await opcua.read_variable(VARIABLES["hc2p3_voltage"])
        pdc3_plim = await opcua.read_variable(VARIABLES["pdc3_plim"])
        
        evi3_cp_status = await opcua.read_variable(VARIABLES["evi3_cp_status"])
        evi3_substatus = await opcua.read_variable(VARIABLES["evi3_substatus"])
        evi3_error = await opcua.read_variable(VARIABLES["evi3_error"])
        evi3_pilot = await opcua.read_variable(VARIABLES["evi3_pilot"])
        evi3_voltage = await opcua.read_variable(VARIABLES["evi3_voltage"])
        evi3_target_current = await opcua.read_variable(VARIABLES["evi3_target_current"])
        evi3_target_voltage = await opcua.read_variable(VARIABLES["evi3_target_voltage"])
        evi3_soc = await opcua.read_variable(VARIABLES["evi3_soc"])
        
        evi3_temp1 = await opcua.read_variable(VARIABLES["evi3_temp1"])
        evi3_temp2 = await opcua.read_variable(VARIABLES["evi3_temp2"])
        dcbm3_temp_h = await opcua.read_variable(VARIABLES["dcbm3_temp_h"])
        dcbm3_temp_l = await opcua.read_variable(VARIABLES["dcbm3_temp_l"])
        
        seq13_ready_class = "success" if seq13_ready else "danger"
        seq13_fault_class = "danger" if seq13_fault else "inactive"
        seq13_ack_class = "cmd-btn"
        
        evi3_ack_class = "cmd-btn"
        evi3_es_class = "cmd-btn"

        ic_translations = decode_bits(seq13_ic, IC_MAP)
        pc_translations = decode_bits(seq13_pc, PC_MAP)
                 
        hmi_state = decode_hmi (seq13_hmi)
        cpstatusCode = decode_CPStatusCode (evi3_cp_status)
        pilotstatusCode = decode_PilotStatus (evi3_pilot)

        ic_html = "<br>".join(ic_translations)
        pc_html = "<br>".join(pc_translations)

        html = f"""
        <div class="seq-section">
            <h4>Sequence 13</h4>
            <div class="data-row">
                <span class="label">Ready</span>
                <span class="indicator {seq13_ready_class}"></span>
            </div>
            <div class="data-row">
                <span class="label">Fault</span>
                <span class="indicator {seq13_fault_class}"></span>
            </div>
           <div class="data-row">
                <span class="label">IC</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{seq13_ic}</span>
                    <div style="font-size: 0.62rem; color: var(--text-secondary); text-align: left;">
                        {ic_html}
                    </div>
                </div>
            </div>

            <div class="data-row">
                <span class="label">PC</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{seq13_pc}</span>
                    <div style="font-size: 0.62rem; color: var(--text-secondary); text-align: left;">
                        {pc_html}
                    </div>
                </div>
            </div>
            <div class="data-row">
                <span class="label">Step</span>
                <span class="value">{seq13_branch}</span>
            </div>
            <div class="data-row">
                <span class="label">HMI</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{seq13_hmi}</span>
                    <span style="font-size: 0.62rem; color: var(--text-secondary);">{hmi_state}</span>
            </div>
            </div>
            <div class="cmd-row">
                <button class="{seq13_ack_class}" hx-post="/api/sequences/seq13/ack" hx-swap="none">Séquence 13 - Ack</button>
            </div>
        </div>
        
        <div class="seq-section">
            <h4>HC2P3</h4>
            <div class="data-row">
                <span class="label">Current Measurement</span>
                <span class="value">{hc2p3_current:.2f} A</span>
            </div>
            <div class="data-row">
                <span class="label">Voltage Measurement</span>
                <span class="value">{hc2p3_voltage:.2f} V</span>
            </div>
            <div class="data-row">
                <span class="label">Power limitation</span>
                <span class="value">{pdc3_plim:.2f} Kw</span>
            </div>
        </div>
        
        <div class="seq-section">
            <h4>EVI3</h4>
            <div class="data-row">
                <span class="label">CP Status Code</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{evi3_cp_status}</span>
                    <span style="font-size: 0.62rem; color: var(--text-secondary);">{cpstatusCode}</span>
                </div>
            </div>
            <div class="data-row">
                <span class="label">Substate</span>
                <span class="value">{evi3_substatus}</span>
            </div>
            <div class="data-row">
                <span class="label">Error Code</span>
                <span class="value">{evi3_error}</span>
            </div>
            <div class="data-row">
                <span class="label">Pilot Status Code</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{evi3_pilot}</span>
                    <span style="font-size: 0.62rem; color: var(--text-secondary);">{pilotstatusCode}</span>
                </div>
            </div>
            <div class="data-row">
                <span class="label">EVI Voltage Measurement</span>
                <span class="value">{evi3_voltage} V</span>
            </div>
            <div class="data-row">
                <span class="label">Target Current</span>
                <span class="value">{evi3_target_current} A</span>
            </div>
            <div class="data-row">
                <span class="label">Target Voltage</span>
                <span class="value">{evi3_target_voltage} V</span>
            </div>
            <div class="data-row">
                <span class="label">SOC</span>
                <span class="value">{evi3_soc} %</span>
            </div>
            <div class="cmd-row">
                <button class="{evi3_ack_class}" hx-post="/api/sequences/evi3/ack" hx-swap="none">EVI - Ack</button>
                <button class="{evi3_es_class}" hx-post="/api/sequences/evi3/es" hx-swap="none">EVI - ES</button>
            </div>
        </div>
        
        <div class="seq-section">
            <h4>Temperature</h4>
            <div class="data-row">
                <span class="label">Temperature pistolet 1</span>
                <span class="value">{evi3_temp1} °C</span>
            </div>
            <div class="data-row">
                <span class="label">Temperature pistolet 2</span>
                <span class="value">{evi3_temp2} °C</span>
            </div>
            <div class="data-row">
                <span class="label">Temperature DCBM_H</span>
                <span class="value">{dcbm3_temp_h} °C</span>
            </div>
            <div class="data-row">
                <span class="label">Temperature DCBM_L</span>
                <span class="value">{dcbm3_temp_l} °C</span>
            </div>
        </div>
        """
        
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f'<div class="seq-section"><span class="label">Error: {str(e)}</span></div>')

@router.get("/api/sequences/pdc4")
async def get_pdc4_data():
    try:
        from main import get_opcua_client
        opcua = get_opcua_client()
        
        seq23_ready = await opcua.read_variable(VARIABLES["seq23_ready"])
        seq23_fault = await opcua.read_variable(VARIABLES["seq23_fault"])
        seq23_ic = await opcua.read_variable(VARIABLES["seq23_ic"])
        seq23_pc = await opcua.read_variable(VARIABLES["seq23_pc"])
        seq23_branch = await opcua.read_variable(VARIABLES["seq23_branch"])
        seq23_ack_val = await opcua.read_variable(VARIABLES["seq23_ack"])
        seq23_hmi = await opcua.read_variable(VARIABLES["seq23_hmi"])

        hc2p4_current = await opcua.read_variable(VARIABLES["hc2p4_current"])
        hc2p4_voltage = await opcua.read_variable(VARIABLES["hc2p4_voltage"])
        pdc4_plim = await opcua.read_variable(VARIABLES["pdc4_plim"])
        
        evi4_cp_status = await opcua.read_variable(VARIABLES["evi4_cp_status"])
        evi4_substatus = await opcua.read_variable(VARIABLES["evi4_substatus"])
        evi4_error = await opcua.read_variable(VARIABLES["evi4_error"])
        evi4_pilot = await opcua.read_variable(VARIABLES["evi4_pilot"])
        evi4_voltage = await opcua.read_variable(VARIABLES["evi4_voltage"])
        evi4_target_current = await opcua.read_variable(VARIABLES["evi4_target_current"])
        evi4_target_voltage = await opcua.read_variable(VARIABLES["evi4_target_voltage"])
        evi4_soc = await opcua.read_variable(VARIABLES["evi4_soc"])
        
        evi4_temp1 = await opcua.read_variable(VARIABLES["evi4_temp1"])
        evi4_temp2 = await opcua.read_variable(VARIABLES["evi4_temp2"])
        dcbm4_temp_h = await opcua.read_variable(VARIABLES["dcbm4_temp_h"])
        dcbm4_temp_l = await opcua.read_variable(VARIABLES["dcbm4_temp_l"])
        
        seq23_ready_class = "success" if seq23_ready else "danger"
        seq23_fault_class = "danger" if seq23_fault else "inactive"
        seq23_ack_class = "cmd-btn"
        
        evi4_ack_class = "cmd-btn"
        evi4_es_class = "cmd-btn"
                         
        hmi_state = decode_hmi (seq23_hmi)
        cpstatusCode = decode_CPStatusCode (evi4_cp_status)
        pilotstatusCode = decode_PilotStatus (evi4_pilot)

        ic_translations = decode_bits(seq23_ic, IC_MAP)
        pc_translations = decode_bits(seq23_pc, PC_MAP)
        
        ic_html = "<br>".join(ic_translations)
        pc_html = "<br>".join(pc_translations)

        html = f"""
        <div class="seq-section">
            <h4>Sequence 23</h4>
            <div class="data-row">
                <span class="label">Ready</span>
                <span class="indicator {seq23_ready_class}"></span>
            </div>
            <div class="data-row">
                <span class="label">Fault</span>
                <span class="indicator {seq23_fault_class}"></span>
            </div>
            <div class="data-row">
                <span class="label">IC</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{seq23_ic}</span>
                    <div style="font-size: 0.62rem; color: var(--text-secondary); text-align: left;">
                        {ic_html}
                    </div>
                </div>
            </div>

            <div class="data-row">
                <span class="label">PC</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{seq23_pc}</span>
                    <div style="font-size: 0.62rem; color: var(--text-secondary); text-align: left;">
                        {pc_html}
                    </div>
                </div>
            </div>
            <div class="data-row">
                <span class="label">Step</span>
                <span class="value">{seq23_branch}</span>
            </div>
            <div class="data-row">
                <span class="label">HMI</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{seq23_hmi}</span>
                    <span style="font-size: 0.62rem; color: var(--text-secondary);">{hmi_state}</span>
                </div>
            </div>
            <div class="cmd-row">
                <button class="{seq23_ack_class}" hx-post="/api/sequences/seq23/ack" hx-swap="none">Séquence 23 - Ack</button>
            </div>
        </div>
        
        <div class="seq-section">
            <h4>HC2P4</h4>
            <div class="data-row">
                <span class="label">Current Measurement</span>
                <span class="value">{hc2p4_current:.2f} A</span>
            </div>
            <div class="data-row">
                <span class="label">Voltage Measurement</span>
                <span class="value">{hc2p4_voltage:.2f} V</span>
            </div>
            <div class="data-row">
                <span class="label">Power limitation</span>
                <span class="value">{pdc4_plim:.2f} Kw</span>
            </div>
        </div>
        
        <div class="seq-section">
            <h4>EVI4</h4>
            <div class="data-row">
                <span class="label">CP Status Code</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{evi4_cp_status}</span>
                    <span style="font-size: 0.62rem; color: var(--text-secondary);">{cpstatusCode}</span>
                </div>
            </div>
            <div class="data-row">
                <span class="label">Substate</span>
                <span class="value">{evi4_substatus}</span>
            </div>
            <div class="data-row">
                <span class="label">Error Code</span>
                <span class="value">{evi4_error}</span>
            </div>
            <div class="data-row">
                <span class="label">Pilot Status Code</span>
                <div style="display: flex; flex-direction: column; gap: 0.2rem; align-items: flex-end;">
                    <span class="value">{evi4_pilot}</span>
                    <span style="font-size: 0.62rem; color: var(--text-secondary);">{pilotstatusCode}</span>
                </div>
            </div>
            <div class="data-row">
                <span class="label">EVI Voltage Measurement</span>
                <span class="value">{evi4_voltage} V</span>
            </div>
            <div class="data-row">
                <span class="label">Target Current</span>
                <span class="value">{evi4_target_current} A</span>
            </div>
            <div class="data-row">
                <span class="label">Target Voltage</span>
                <span class="value">{evi4_target_voltage} V</span>
            </div>
            <div class="data-row">
                <span class="label">SOC</span>
                <span class="value">{evi4_soc} %</span>
            </div>
            <div class="cmd-row">
                <button class="{evi4_ack_class}" hx-post="/api/sequences/evi4/ack" hx-swap="none">EVI - Ack</button>
                <button class="{evi4_es_class}" hx-post="/api/sequences/evi4/es" hx-swap="none">EVI - ES</button>
            </div>
        </div>
        
        <div class="seq-section">
            <h4>Temperature</h4>
            <div class="data-row">
                <span class="label">Temperature pistolet 1</span>
                <span class="value">{evi4_temp1} °C</span>
            </div>
            <div class="data-row">
                <span class="label">Temperature pistolet 2</span>
                <span class="value">{evi4_temp2} °C</span>
            </div>
            <div class="data-row">
                <span class="label">Temperature DCBM_H</span>
                <span class="value">{dcbm4_temp_h} °C</span>
            </div>
            <div class="data-row">
                <span class="label">Temperature DCBM_L</span>
                <span class="value">{dcbm4_temp_l} °C</span>
            </div>
        </div>
        """
        
        return HTMLResponse(html)
    except Exception as e:
        return HTMLResponse(f'<div class="seq-section"><span class="label">Error: {str(e)}</span></div>')

IC_MAP = {
    0: "IC00 - Main sequence running",
    1: "IC01 - Ev contactor not closed",
    2: "IC02 - No over temp Self",
    6: "IC06 - EndPoint OCPP Connected",
    7: "IC07 - HMI communication Fault",
    8: "IC08 - Not charging",
    9: "IC09 - DCBM Fault",
    10: "IC10 - Unavailable from CPO",
    11: "IC11 - Payter Com Fault",
    12: "IC12 - ZMQ Com Fault",
}

PC_MAP = {
    0: "PC00 - RIO COM",
    2: "PC02 - Inverter M1 Ready",
    3: "PC03 - UpstreamSequence no fault",
    4: "PC04 - Ev contactor no discordance",
    6: "PC06 - No over temp Self",
    7: "PC07 - No TO",
    8: "PC08 - Plug no Over Temp CCS",
    9: "PC09 - Inverter OverVoltage",
    12: "PC12 - Communication EVI",
    13: "PC13 - ES EVI",
    14: "PC14 - Manual Indispo",
    15: "PC15 - HMI communication Fault",
}

HMI = {
    1: "Vue Principale",
    10: "Vue Identification",
    20: "Vue Branchez Cable",
    30: "Vue Charge",
    32: "Vue End charge",
    40: "Vue Identification",
    60: "Vue Débranchez Cable",
    70: "Vue Résumé",
}

CPStatusCode = {
    1: "INIT",
    2: "Handcheck",
    4: "LockConnector",
    6: "LockConnector",
    7: "CableCheck",
    8: "Charge",
    10: "End charge",
    14: "WeldingDetection",
    15: "WaitUnplug",
    17: "Fault",
    18: "Reset Fault",
}

PilotStatus = {
    0: "Voiture déconnectée",
    1: "Voiture connectée",
    2: "Voiture en charge",
    5: "État Fault",
}

def decode_hmi(value):
    return HMI.get(value, f"Unknown ({value})")

def decode_CPStatusCode(value):
    return CPStatusCode.get(value, f"Unknown ({value})")

def decode_PilotStatus(value):
    return PilotStatus.get(value, f"Unknown ({value})")

def decode_bits(value, bit_map):
    active_bits = []
    for bit, description in bit_map.items():
        if value & (1 << bit):
            active_bits.append(description)
    return active_bits

async def set_variable(variable_name: str, value: bool):
    from main import get_opcua_client
    opcua = get_opcua_client()
    await opcua.write_variable(variable_name, value)

"""
on garde si jamais
async def pulse_ack(variable_name: str):
    from main import get_opcua_client
    opcua = get_opcua_client()
    
    for _ in range(10):
        await opcua.write_variable(variable_name, True)
        await asyncio.sleep(0.1)
"""

async def pulse_startstop(variable_name: str):
    from main import get_opcua_client
    opcua = get_opcua_client()
    
    await opcua.write_variable(variable_name, True)
    await asyncio.sleep(3)
    await opcua.write_variable(variable_name, False)

@router.post("/api/sequences/{seq}/{cmd}")
async def execute_command(seq: str, cmd: str, background_tasks: BackgroundTasks):
    try:
        key = f"{seq}_{cmd}"
        variable_name = VARIABLES[key]

        if cmd in FAST_PULSE_COMMANDS or key in FAST_PULSE_COMMANDS:
            background_tasks.add_task(set_variable, variable_name, True)
        else:
            background_tasks.add_task(pulse_startstop, variable_name)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))