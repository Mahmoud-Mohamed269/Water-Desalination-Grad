#include "alert_engine.h"
#include "config.h"

// ============================================================
// pushAlert — local alert handling (e.g. Serial print)
// ============================================================
bool pushAlert(const Alert& a) {
    Serial.printf("[ALERT] %s (%s): %s = %.2f (Thresh: %.2f) - %s\n", 
        a.type.c_str(), a.severity.c_str(), a.parameter.c_str(), a.value, a.threshold, a.message.c_str());
    return true;
}

// ============================================================
// Cooldown Tracking — prevents alert spam for same parameter
// ============================================================
static unsigned long lastAlertTime_pH       = 0;
static unsigned long lastAlertTime_TDS      = 0;
static unsigned long lastAlertTime_Turbidity = 0;
static unsigned long lastAlertTime_Temp     = 0;
static unsigned long lastAlertTime_Flow     = 0;
static unsigned long lastAlertTime_Pressure = 0;

const unsigned long ALERT_COOLDOWN_MS = 60000; // 1 minute between repeat alerts

// ============================================================
// alertEngineInit — Reset all cooldown timers
// ============================================================
void alertEngineInit() {
    lastAlertTime_pH        = 0;
    lastAlertTime_TDS       = 0;
    lastAlertTime_Turbidity = 0;
    lastAlertTime_Temp      = 0;
    lastAlertTime_Flow      = 0;
    lastAlertTime_Pressure  = 0;
}

// ============================================================
// checkAlerts — Evaluate all sensor thresholds and push alerts
// ============================================================
void checkAlerts(const SensorReading& r, const String& timestamp) {
    unsigned long now = millis();

    // --------------------------------------------------------
    // pH Alerts (feed & permeate)
    // --------------------------------------------------------
    if (now - lastAlertTime_pH >= ALERT_COOLDOWN_MS) {
        float worst_low  = min(r.ph_feed, r.ph_permeate);
        float worst_high = max(r.ph_feed, r.ph_permeate);

        if (worst_low < ALERT_PH_MIN) {
            Alert a = {"low_ph", "warning", "ph", worst_low, ALERT_PH_MIN,
                       "pH is below minimum safe threshold", timestamp};
            if (worst_low < ALERT_PH_CRITICAL_MIN) a.severity = "critical";
            if (pushAlert(a)) lastAlertTime_pH = now;
        } else if (worst_high > ALERT_PH_MAX) {
            Alert a = {"high_ph", "warning", "ph", worst_high, ALERT_PH_MAX,
                       "pH is above maximum safe threshold", timestamp};
            if (worst_high > ALERT_PH_CRITICAL_MAX) a.severity = "critical";
            if (pushAlert(a)) lastAlertTime_pH = now;
        }
    }

    // --------------------------------------------------------
    // TDS Alerts (feed & permeate)
    // --------------------------------------------------------
    if (now - lastAlertTime_TDS >= ALERT_COOLDOWN_MS) {
        float worst_tds = max(r.tds_feed, r.tds_permeate);
        if (worst_tds > ALERT_TDS_WARNING) {
            Alert a = {"high_tds", "warning", "tds", worst_tds, (float)ALERT_TDS_MAX,
                       "TDS is above warning threshold", timestamp};
            if (worst_tds > ALERT_TDS_CRITICAL) a.severity = "critical";
            else if (worst_tds > ALERT_TDS_MAX)  a.severity = "critical";
            if (pushAlert(a)) lastAlertTime_TDS = now;
        }
    }

    // --------------------------------------------------------
    // Turbidity Alerts (feed line)
    // --------------------------------------------------------
    if (now - lastAlertTime_Turbidity >= ALERT_COOLDOWN_MS) {
        if (r.turbidity_feed > ALERT_TURBIDITY_WARNING) {
            Alert a = {"high_turbidity", "warning", "turbidity", r.turbidity_feed, ALERT_TURBIDITY_MAX,
                       "Feed turbidity is high — check pre-filter", timestamp};
            if (r.turbidity_feed > ALERT_TURBIDITY_CRITICAL) a.severity = "critical";
            if (pushAlert(a)) lastAlertTime_Turbidity = now;
        }
    }

    // --------------------------------------------------------
    // Temperature Alerts (feed & permeate)
    // --------------------------------------------------------
    if (now - lastAlertTime_Temp >= ALERT_COOLDOWN_MS) {
        float worst_high = max(r.temperature_feed, r.temperature_permeate);
        float worst_low  = min(r.temperature_feed, r.temperature_permeate);

        if (worst_high > ALERT_TEMP_MAX) {
            Alert a = {"high_temp", "warning", "temperature", worst_high, ALERT_TEMP_MAX,
                       "Water temperature is high — membrane performance may degrade", timestamp};
            if (worst_high > ALERT_TEMP_CRITICAL) a.severity = "critical";
            if (pushAlert(a)) lastAlertTime_Temp = now;
        } else if (worst_low < ALERT_TEMP_MIN) {
            Alert a = {"low_temp", "warning", "temperature", worst_low, ALERT_TEMP_MIN,
                       "Water temperature is below safe operating range", timestamp};
            if (pushAlert(a)) lastAlertTime_Temp = now;
        }
    }

    // --------------------------------------------------------
    // Flow Rate Alerts (feed only — pump must be running)
    // --------------------------------------------------------
    if (now - lastAlertTime_Flow >= ALERT_COOLDOWN_MS) {
        if (r.pump_status == "running") {
            if (r.flow_rate_feed < ALERT_FLOW_MIN) {
                Alert a = {"low_flow", "critical", "flow_rate", r.flow_rate_feed, ALERT_FLOW_MIN,
                           "Feed flow rate is critically low — possible blockage or pump failure", timestamp};
                if (pushAlert(a)) lastAlertTime_Flow = now;
            } else if (r.flow_rate_feed > ALERT_FLOW_MAX) {
                Alert a = {"high_flow", "warning", "flow_rate", r.flow_rate_feed, ALERT_FLOW_MAX,
                           "Feed flow rate is abnormally high — possible leak or bypass", timestamp};
                if (pushAlert(a)) lastAlertTime_Flow = now;
            }
        }
    }

    // --------------------------------------------------------
    // Pressure Alerts (feed line)
    // --------------------------------------------------------
    if (now - lastAlertTime_Pressure >= ALERT_COOLDOWN_MS) {
        if (r.pressure_feed > ALERT_PRESSURE_MAX) {
            Alert a = {"high_pressure", "warning", "pressure", r.pressure_feed, ALERT_PRESSURE_MAX,
                       "Feed pressure is above safe operating limit", timestamp};
            if (r.pressure_feed > ALERT_PRESSURE_CRITICAL) a.severity = "critical";
            if (pushAlert(a)) lastAlertTime_Pressure = now;
        }
    }
}
