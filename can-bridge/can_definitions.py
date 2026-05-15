"""CAN signal definitions for PSA vehicles.

Each entry: (name, byte_offset, bit_offset, bit_length, scale, offset, unit, enum_map)
enum_map: dict mapping raw int to display string, or None for numeric.
"""

CAN_DEFINITIONS = {}

# ---------------------------------------------------------------------------
# Drivetrain
# ---------------------------------------------------------------------------

CAN_DEFINITIONS[0x0B6] = [
    ("rpm",              0, 0, 16, 1, 0, "rpm", None),
    ("speed",            2, 0, 16, 0.1, 0, "km/h", None),
    ("distance_cmb",     4, 0, 16, 1, 0, "km", None),
    ("consumption_cmb",  6, 0, 8, 0.1, 0, "L/100km", None),
    ("info_valid",       7, 7, 1, 1, 0, "", {0: "invalid", 1: "valid"}),
]

CAN_DEFINITIONS[0x0F6] = [
    ("engine_status",    0, 0, 2, 1, 0, "", {0: "stopped", 1: "starting", 2: "running", 3: "fault"}),
    ("generator_status", 0, 2, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("key_position",     0, 3, 2, 1, 0, "", {0: "stop", 1: "contact", 2: "starter", 3: "free"}),
    ("factory_mode",     0, 5, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("config_mode",      0, 6, 2, 1, 0, "", {0: "factory", 1: "free1", 2: "client", 3: "free2"}),
    ("coolant_temp",     1, 0, 8, 1, -40, "degC", None),
    ("mileage",          2, 0, 24, 1, 0, "km", None),
    ("external_temp",    6, 0, 8, 1, -40, "degC", None),
    ("left_turn",        7, 0, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("right_turn",       7, 1, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("wiper",            7, 6, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("reverse_light",    7, 7, 1, 1, 0, "", {0: "off", 1: "on"}),
]

CAN_DEFINITIONS[0x128] = [
    ("service_blink",           0, 0, 1, 1, 0, "", {0: "off", 1: "blinking"}),
    ("passenger_seatbelt",      0, 1, 1, 1, 0, "", {0: "ok", 1: "warning"}),
    ("diesel_preheat",          0, 2, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("fuel_circuit_neutral",    0, 3, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("fuel_level_low",          0, 4, 1, 1, 0, "", {0: "ok", 1: "low"}),
    ("handbrake",               0, 5, 1, 1, 0, "", {0: "off", 1: "applied"}),
    ("driver_seatbelt",         0, 6, 1, 1, 0, "", {0: "ok", 1: "warning"}),
    ("passenger_airbag_off",    0, 7, 1, 1, 0, "", {0: "active", 1: "deactivated"}),
    ("rear_seatbelt_warn",      1, 0, 1, 1, 0, "", {0: "ok", 1: "warning"}),
    ("abs_active",              1, 1, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("stop_light",              1, 6, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("service_indicator",       1, 7, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("ready_lamp",              2, 0, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("warning_light",           2, 1, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("suspension_status_light", 2, 2, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("esp_in_progress",         2, 3, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("esp_deactivated",         2, 4, 1, 1, 0, "", {0: "off", 1: "deactivated"}),
    ("child_security",          2, 5, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("drl",                     4, 0, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("turn_left",               4, 1, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("turn_right",              4, 2, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("rear_fog",                4, 3, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("front_fog",               4, 4, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("high_beam",               4, 5, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("low_beam",                4, 6, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("parking_light",           4, 7, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("gear_position",           6, 1, 3, 1, 0, "", {
        0: "P", 1: "R", 2: "N", 3: "D", 4: "6", 5: "5", 6: "4",
        7: "3", 8: "2", 9: "1", 15: "-"
    }),
    ("gear_mode",               7, 4, 3, 1, 0, "", {
        0: "Auto", 1: "-", 2: "Sport", 4: "Seq", 5: "Seq Sport", 6: "Snow"
    }),
]

CAN_DEFINITIONS[0x161] = [
    ("oil_level_restart", 0, 7, 1, 1, 0, "", {0: "ok", 1: "restart needed"}),
    ("oil_temp",          2, 0, 8, 1, -40, "degC", None),
    ("fuel_level",        3, 0, 8, 1, 0, "%", None),
    ("oil_level",         6, 0, 8, 1, 0, "%", None),
]

CAN_DEFINITIONS[0x221] = [
    ("stick_left",              0, 0, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("stick_right",             0, 3, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("remaining_range_invalid", 0, 6, 1, 1, 0, "", {0: "valid", 1: "invalid"}),
    ("consumption_invalid",     0, 7, 1, 1, 0, "", {0: "valid", 1: "invalid"}),
    ("instant_consumption",     1, 0, 16, 0.1, 0, "L/100km", None),
    ("remaining_range",         3, 0, 16, 1, 0, "km", None),
    ("total_range",             5, 0, 16, 1, 0, "km", None),
]

CAN_DEFINITIONS[0x261] = [
    ("trip2_avg_speed",     0, 0, 8, 1, 0, "km/h", None),
    ("trip2_distance",      1, 0, 16, 1, 0, "km", None),
    ("trip2_consumption",   3, 0, 16, 0.1, 0, "L/100km", None),
    ("trip2_last_reset",    5, 0, 16, 1, 0, "km", None),
]

CAN_DEFINITIONS[0x2A1] = [
    ("trip1_avg_speed",     0, 0, 8, 1, 0, "km/h", None),
    ("trip1_distance",      1, 0, 16, 1, 0, "km", None),
    ("trip1_consumption",   3, 0, 16, 0.1, 0, "L/100km", None),
    ("trip1_last_reset",    5, 0, 16, 1, 0, "km", None),
]

CAN_DEFINITIONS[0x167] = [
    ("trip_data_on_odometer", 0, 0, 3, 1, 0, "", {0: "none", 1: "general", 2: "trip1", 4: "trip2", 7: "not managed"}),
    ("reset_maintenance",     0, 3, 1, 1, 0, "", {0: "off", 1: "reset"}),
    ("emergency_call",        0, 4, 1, 1, 0, "", {0: "off", 1: "in progress"}),
    ("alert_reminder",        0, 5, 1, 1, 0, "", {0: "off", 1: "requested"}),
    ("reset_trip2",           0, 6, 1, 1, 0, "", {0: "off", 1: "reset"}),
    ("reset_trip1",           0, 7, 1, 1, 0, "", {0: "off", 1: "reset"}),
    ("total_distance",        2, 0, 16, 1, 0, "km", None),
    ("interactive_msg",       4, 0, 8, 1, 0, "", None),
]

# ---------------------------------------------------------------------------
# Lights
# ---------------------------------------------------------------------------

CAN_DEFINITIONS[0x361] = [
    ("profile_number",             0, 0, 3, 1, 0, "", None),
    ("profile_change_disabled",    0, 3, 1, 1, 0, "", {0: "enabled", 1: "disabled"}),
    ("permanent_rear_flap_lock",   1, 0, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("partial_windows",            1, 1, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("welcome_function",           1, 2, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("securoscope",                1, 3, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("key_config_enabled",         1, 4, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("auto_lighting",              2, 0, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("irc_present",                2, 1, 1, 1, 0, "", {0: "no", 1: "yes"}),
    ("auto_electric_brake",        2, 2, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("motorway_lighting",          2, 3, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("follow_me_home",             2, 4, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("lock_on_go",                 2, 5, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("auto_distance_closure",      2, 6, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("rear_wiper_option",          3, 5, 1, 1, 0, "", {0: "no", 1: "yes"}),
    ("drl_present",                3, 6, 1, 1, 0, "", {0: "no", 1: "yes"}),
    ("blindspot_monitoring",       4, 1, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("ambient_lighting",           4, 2, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("emf_present",                4, 4, 1, 1, 0, "", {0: "no", 1: "yes"}),
    ("aas_disable",                4, 5, 1, 1, 0, "", {0: "enabled", 1: "disabled"}),
    ("aas_audible",                4, 6, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("aas_visual",                 4, 7, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("braking_on_alarm_risk",      5, 1, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("tpms_reset_present",         5, 2, 1, 1, 0, "", {0: "no", 1: "yes"}),
    ("tpms_present",               5, 4, 3, 1, 0, "", None),
]

# ---------------------------------------------------------------------------
# Doors & Body
# ---------------------------------------------------------------------------

CAN_DEFINITIONS[0x0E8] = [
    ("hood_open",                  0, 0, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("rear_left_door_open",        0, 1, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("rear_right_door_open",       0, 2, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("front_left_door_open",       0, 3, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("front_right_door_open",      0, 4, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("door_alert_above_10kmph",    0, 5, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("door_alert_below_10kmph",    0, 6, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("key_alert",                  0, 7, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("esp_alert_enabled",          1, 0, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("handbrake_accelerating",     1, 1, 1, 1, 0, "", {0: "off", 1: "warning"}),
    ("fuel_flap_open_below_10",    1, 2, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("bva_safety_alert",           1, 3, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("vehicle_type",               1, 4, 1, 1, 0, "", {0: "5-door", 1: "3-door"}),
    ("fuel_flap_open_above_10",    1, 5, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("rear_window_open",           1, 6, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("trunk_open",                 1, 7, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("body_position_final",        2, 0, 3, 1, 0, "", {0: "normal", 1: "mid-high", 2: "low", 3: "high", 7: "-"}),
    ("body_movement_nature",       2, 3, 2, 1, 0, "", {0: "none", 1: "ascending", 2: "descending", 3: "refused"}),
    ("suspension_movement_alert",  2, 5, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("foot_on_brake_alert",        2, 6, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("esp_alert_disabled",         2, 7, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("off_suspension_alert",       3, 0, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("on_suspension_alert",        3, 1, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("body_position_real",         3, 2, 3, 1, 0, "", {0: "normal", 1: "mid-high", 2: "low", 3: "high", 7: "-"}),
    ("body_position_initial",      3, 5, 3, 1, 0, "", {0: "normal", 1: "mid-high", 2: "low", 3: "high", 7: "-"}),
    ("child_safety_deactivated",   4, 0, 1, 1, 0, "", {0: "off", 1: "deactivated"}),
    ("windscreen_washer_low",      4, 3, 1, 1, 0, "", {0: "ok", 1: "low"}),
    ("auto_wiper_alert_disabled",  4, 4, 1, 1, 0, "", {0: "off", 1: "disabled"}),
    ("auto_wiper_alert_enabled",   4, 5, 1, 1, 0, "", {0: "off", 1: "enabled"}),
    ("auto_lighting_alert_disabled", 4, 6, 1, 1, 0, "", {0: "off", 1: "disabled"}),
    ("auto_lighting_alert_enabled", 4, 7, 1, 1, 0, "", {0: "off", 1: "enabled"}),
    ("child_safety_activated",     5, 0, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("lights_reminder",            5, 1, 1, 1, 0, "", {0: "off", 1: "active"}),
]

CAN_DEFINITIONS[0x220] = [
    ("fuel_flap_open",        0, 0, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("rear_window_open",      0, 1, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("hood_open",             0, 2, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("trunk_open",            0, 3, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("rear_right_door_open",  0, 4, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("rear_left_door_open",   0, 5, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("front_right_door_open", 0, 6, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("front_left_door_open",  0, 7, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("spare_wheel_status",    1, 6, 1, 1, 0, "", {0: "ok", 1: "warning"}),
    ("vehicle_type",          1, 7, 1, 1, 0, "", {0: "5-door", 1: "3-door"}),
]

CAN_DEFINITIONS[0x1A1] = [
    ("show_popup",        0, 0, 8, 1, 0, "", None),
    ("popup_message",     1, 0, 8, 1, 0, "", None),
    ("priority",          2, 0, 4, 1, 0, "", None),
    ("check_in_progress", 2, 4, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("show_on_vth",       2, 5, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("show_on_cmb",       2, 6, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("show_on_emf",       2, 7, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("bonnet_open",       3, 2, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("trunk_open",        3, 3, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("rear_left_open",    3, 4, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("rear_right_open",   3, 5, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("front_left_open",   3, 6, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("front_right_open",  3, 7, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("fuel_flap_open",    4, 6, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("rear_screen_open",  4, 7, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("km_to_display",     5, 0, 16, 1, 0, "km", None),
]

# ---------------------------------------------------------------------------
# Safety & Warnings
# ---------------------------------------------------------------------------

CAN_DEFINITIONS[0x0E6] = [
    ("abr_fault",                   0, 0, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("brake_fluid_level_alert",     0, 1, 1, 1, 0, "", {0: "ok", 1: "low"}),
    ("brake_pads_worn",             0, 2, 1, 1, 0, "", {0: "ok", 1: "worn"}),
    ("slip_alert",                  0, 3, 2, 1, 0, "", {0: "none", 1: "light", 2: "medium", 3: "high"}),
    ("abs_in_progress",             0, 5, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("ree_fault",                   0, 7, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("rear_left_counter",           1, 0, 15, 1, 0, "", None),
    ("rear_left_counter_failure",   2, 0, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("rear_right_counter",          3, 0, 15, 1, 0, "", None),
    ("rear_right_counter_failure",  4, 0, 1, 1, 0, "", {0: "ok", 1: "fault"}),
]

CAN_DEFINITIONS[0x120] = [
    ("menu_available",              0, 2, 2, 1, 0, "", None),
    ("total_blocks",                0, 4, 2, 1, 0, "", None),
    ("block_number",                0, 6, 2, 1, 0, "", None),
    ("high_speed_check_tyre",       1, 1, 1, 1, 0, "", {0: "ok", 1: "check"}),
    ("fuel_tank_access_lock_error", 1, 4, 1, 1, 0, "", {0: "ok", 1: "error"}),
    ("rear_screen_open",            1, 5, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("bonnet_open",                 1, 6, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("boot_open",                   1, 7, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("directional_headlamps_fault", 2, 1, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("bonnet_open2",                2, 2, 1, 1, 0, "", {0: "closed", 1: "open"}),
    ("adjustable_wing_fault",       2, 3, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("parking_brake_faulty",        2, 4, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("gearbox_fault_repair",        3, 2, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("suspension_fault_90kmh",      4, 1, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("engine_fault_repair",         4, 2, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("tyre_pressures_too_low",      4, 4, 1, 1, 0, "", {0: "ok", 1: "low"}),
    ("anti_wander_fault",           4, 6, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("rear_lh_tyre_not_monitored",  5, 0, 1, 1, 0, "", {0: "monitored", 1: "not monitored"}),
    ("rear_rh_tyre_not_monitored",  5, 1, 1, 1, 0, "", {0: "monitored", 1: "not monitored"}),
    ("front_rh_tyre_not_monitored", 5, 2, 1, 1, 0, "", {0: "monitored", 1: "not monitored"}),
    ("front_lh_tyre_not_monitored", 5, 3, 1, 1, 0, "", {0: "monitored", 1: "not monitored"}),
    ("engine_fault_stop_vehicle",   6, 2, 1, 1, 0, "", {0: "ok", 1: "stop!"}),
    ("power_steering_faulty",       6, 6, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("suspension_faulty",           6, 7, 1, 1, 0, "", {0: "ok", 1: "fault"}),
]

CAN_DEFINITIONS[0x168] = [
    ("dsg_fault",               0, 0, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("auto_gearbox_alert",      0, 1, 1, 1, 0, "", {0: "ok", 1: "alert"}),
    ("brake_fluid_alert",       0, 2, 1, 1, 0, "", {0: "ok", 1: "low"}),
    ("oil_pressure_alert",      0, 3, 1, 1, 0, "", {0: "ok", 1: "low"}),
    ("oil_level_alert",         0, 4, 1, 1, 0, "", {0: "ok", 1: "low"}),
    ("coolant_level_alert",     0, 5, 1, 1, 0, "", {0: "ok", 1: "low"}),
    ("oil_temp_max",            0, 6, 1, 1, 0, "", {0: "ok", 1: "max"}),
    ("coolant_temp_max",        0, 7, 1, 1, 0, "", {0: "ok", 1: "max"}),
    ("max_rpm_2",               1, 0, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("minc_blinking",           1, 1, 1, 1, 0, "", {0: "off", 1: "blinking"}),
    ("max_rpm_1",               1, 2, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("auto_wiping_active",      1, 3, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("fap_clogged",             1, 4, 1, 1, 0, "", {0: "ok", 1: "clogged"}),
    ("diesel_additive_alert",   1, 5, 1, 1, 0, "", {0: "ok", 1: "low"}),
    ("tyre_punctured",          1, 6, 1, 1, 0, "", {0: "ok", 1: "punctured"}),
    ("tyre_pressure_low",       1, 7, 1, 1, 0, "", {0: "ok", 1: "low"}),
    ("water_in_diesel",         3, 0, 1, 1, 0, "", {0: "ok", 1: "water!"}),
    ("mil_on",                  3, 1, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("brake_pad_fault",         3, 2, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("gearbox_fault",           3, 3, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("esp_fault",               3, 4, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("abs_fault",               3, 5, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("serious_suspension_fault", 3, 6, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("serious_ehb_fault",       3, 7, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("lamp_bulb_fault",         4, 0, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("generator_fault",         4, 1, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("battery_charge_fault",    4, 2, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("diesel_additive_fault",   4, 3, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("antipollution_fault",     4, 4, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("driver_airbag_fault",     4, 5, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("scr_indicator",           4, 6, 2, 1, 0, "", None),
    ("engine_fault",            5, 0, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("curve_code_fault",        5, 2, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("caar_lamp_status",        5, 3, 2, 1, 0, "", None),
    ("gear_position_driving",   5, 5, 3, 1, 0, "", None),
    ("stt_lamp_status",         6, 0, 2, 1, 0, "", None),
    ("engine_fault_blinking",   6, 2, 1, 1, 0, "", {0: "off", 1: "blinking"}),
    ("fse_tightening_fault",    6, 3, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("fse_system_fault",        6, 4, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("power_steering_fault",    6, 5, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("zev_hybrid",              7, 2, 2, 1, 0, "", None),
    ("ready_status",            7, 6, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("pare_fault",              7, 7, 1, 1, 0, "", {0: "ok", 1: "fault"}),
]

# ---------------------------------------------------------------------------
# Suspension & Steering
# ---------------------------------------------------------------------------

CAN_DEFINITIONS[0x10B] = [
    ("steering_angle",      0, 0, 16, 0.1, -2048, "deg", None),
    ("rotation_speed",      2, 0, 8, 1, 0, "deg/s", None),
    ("is_calibrated",       3, 1, 1, 1, 0, "", {0: "no", 1: "yes"}),
    ("is_adjusted",         3, 2, 1, 1, 0, "", {0: "no", 1: "yes"}),
    ("fault_code",          3, 3, 4, 1, 0, "", None),
    ("rotation_direction",  3, 7, 1, 1, 0, "", {0: "counter-clockwise", 1: "clockwise"}),
]

CAN_DEFINITIONS[0x036] = [
    ("memory_slot_1",             0, 0, 4, 1, 0, "", None),
    ("memory_ordered_1",          0, 4, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("passenger_memory_recall_1", 0, 5, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("ihm_profile_1",             0, 6, 2, 1, 0, "", None),
    ("memory_slot_2",             1, 0, 4, 1, 0, "", None),
    ("memory_ordered_2",          1, 4, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("passenger_memory_recall_2", 1, 5, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("ihm_profile_2",             1, 6, 2, 1, 0, "", None),
    ("economy_mode",              2, 7, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("dashboard_brightness",      3, 0, 4, 1, 0, "", None),
    ("black_panel_status",        3, 4, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("night_mode",                3, 5, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("ignition_mode",             4, 0, 3, 1, 0, "", {0: "standby", 1: "normal", 2: "standby soon", 3: "wake-up", 4: "com-off"}),
    ("prevent_fault_log",         4, 3, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("network_supervision",       4, 5, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("global_fault_clearance",    4, 6, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("activate_rear_camera",      6, 3, 1, 1, 0, "", {0: "off", 1: "on"}),
]

CAN_DEFINITIONS[0x2E1] = [
    ("auto_door_locking_status",  0, 0, 2, 1, 0, "", {0: "absent", 1: "inactive", 2: "-", 3: "active"}),
    ("auto_headlight_status",     0, 2, 2, 1, 0, "", {0: "absent", 1: "inactive", 2: "-", 3: "active"}),
    ("passenger_airbag_status",   0, 4, 2, 1, 0, "", {0: "absent", 1: "inactive", 2: "-", 3: "active"}),
    ("parking_aid_status",        0, 6, 2, 1, 0, "", {0: "absent", 1: "inactive", 2: "-", 3: "active"}),
    ("suspension_mode",           1, 0, 2, 1, 0, "", {0: "absent", 1: "sport", 2: "normal", 3: "-"}),
    ("auto_wiper_status",         1, 2, 2, 1, 0, "", {0: "absent", 1: "inactive", 2: "-", 3: "active"}),
    ("esp_status",                1, 4, 2, 1, 0, "", {0: "absent", 1: "inactive", 2: "-", 3: "active"}),
    ("door_locking_status",       1, 6, 2, 1, 0, "", {0: "absent", 1: "inactive", 2: "-", 3: "active"}),
    ("start_stop_status",         2, 2, 2, 1, 0, "", {0: "absent", 1: "inactive", 2: "-", 3: "active"}),
    ("child_safety_status",       2, 6, 2, 1, 0, "", {0: "absent", 1: "inactive", 2: "-", 3: "active"}),
    ("roof_status",               2, 3, 3, 1, 0, "", {0: "no display", 1: "coupe", 2: "boot open roof open", 3: "boot open roof in boot", 4: "convertible", 5: "boot open roof closed"}),
    ("suspension_movement",       3, 0, 2, 1, 0, "", {0: "none", 1: "rise", 2: "descent", 3: "refused"}),
    ("suspension_final_position", 3, 2, 3, 1, 0, "", {0: "normal", 1: "mid", 2: "low", 3: "high", 7: "-"}),
    ("suspension_initial_position", 3, 5, 3, 1, 0, "", {0: "normal", 1: "mid", 2: "low", 3: "high", 7: "-"}),
    ("suspension_alarm",          4, 4, 1, 1, 0, "", {0: "off", 1: "alarm"}),
    ("suspension_actual_position", 4, 5, 3, 1, 0, "", {0: "normal", 1: "mid", 2: "low", 3: "high", 7: "-"}),
]

# ---------------------------------------------------------------------------
# Climate
# ---------------------------------------------------------------------------

CAN_DEFINITIONS[0x1E3] = [
    ("separate_sides",        0, 0, 1, 1, 0, "", {0: "linked", 1: "separate"}),
    ("recycling_on_pushed",   0, 1, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("auto_speed",            0, 2, 1, 1, 0, "", {0: "off", 1: "auto"}),
    ("auto_mode",             0, 3, 1, 1, 0, "", {0: "off", 1: "auto"}),
    ("airflow_auto",          0, 4, 1, 1, 0, "", {0: "off", 1: "auto"}),
    ("ac_off",                0, 5, 1, 1, 0, "", {0: "on", 1: "off"}),
    ("ac_compressor_off",     0, 6, 1, 1, 0, "", {0: "on", 1: "off"}),
    ("recycling_on",          0, 7, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("rear_window_heating",   1, 3, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("center_temperature",    1, 4, 3, 1, 0, "", None),
    ("windshield",            1, 7, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("temperature_left",      2, 0, 8, 1, 0, "", None),
    ("temperature_right",     3, 0, 8, 1, 0, "", None),
    ("air_direction_left",    4, 0, 8, 1, 0, "", None),
    ("air_direction_right",   5, 0, 8, 1, 0, "", None),
    ("fan_speed",             6, 0, 8, 1, 0, "", None),
]

# ---------------------------------------------------------------------------
# Driver Aids
# ---------------------------------------------------------------------------

CAN_DEFINITIONS[0x0E1] = [
    ("measurement_side",      0, 0, 2, 1, 0, "", {0: "inactive", 1: "left", 2: "right"}),
    ("front_status",          0, 2, 3, 1, 0, "", {0: "undefined", 1: "fault", 2: "disabled", 4: "active", 5: "wait", 6: "out of service"}),
    ("rear_status",           0, 5, 3, 1, 0, "", {0: "undefined", 1: "fault", 2: "disabled", 4: "active", 5: "wait", 6: "out of service"}),
    ("sound_enabled",         1, 4, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("sound_location",        1, 5, 1, 1, 0, "", {0: "rear", 1: "front"}),
    ("beep_channel",          1, 6, 2, 1, 0, "", {0: "none", 1: "left", 2: "right", 3: "both"}),
    ("beep_delay",            2, 0, 6, 1, 0, "ms", None),
    ("beep_duration",         2, 6, 2, 1, 0, "", {0: "1", 1: "2", 2: "3", 3: "4"}),
    ("rear_distance",         3, 2, 3, 1, 0, "bars", None),
    ("rear_left_distance",    3, 5, 3, 1, 0, "bars", None),
    ("front_left_distance",   4, 2, 3, 1, 0, "bars", None),
    ("rear_right_distance",   4, 5, 3, 1, 0, "bars", None),
    ("show_on_display",       5, 1, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("front_right_distance",  5, 2, 3, 1, 0, "bars", None),
    ("front_distance",        5, 5, 3, 1, 0, "bars", None),
    ("measurement_status",    6, 5, 3, 1, 0, "", {2: "off", 4: "active"}),
    ("measured_free_space",   6, 3, 2, 1, 0, "", {0: "none", 1: "small", 2: "medium", 3: "large"}),
]

CAN_DEFINITIONS[0x1A8] = [
    ("setting_status",              0, 0, 1, 1, 0, "", {0: "no adjustment", 1: "adjustment"}),
    ("unit_of_speed",               0, 1, 1, 1, 0, "", {0: "km/h", 1: "mph"}),
    ("activate_function",           0, 2, 1, 1, 0, "", {0: "off", 1: "activate"}),
    ("status_of_selected_function", 0, 3, 3, 1, 0, "", None),
    ("selected_function",           0, 6, 2, 1, 0, "", None),
    ("cruise_control_speed",        1, 0, 16, 1, 0, "km/h", None),
    ("trip_cmb",                    5, 0, 24, 1, 0, "km", None),
]

CAN_DEFINITIONS[0x227] = [
    ("amvar_sport_led",          0, 0, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("child_lock_led",           0, 2, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("esp_led",                  0, 4, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("aas_led",                  0, 6, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("ac_on_led",                1, 0, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("rear_window_heating_led",  1, 2, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("stl_led",                  1, 4, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("secondary_brake_led",      1, 6, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("blind_spot_monitoring_led", 2, 0, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("ac_airflow_type",          2, 2, 2, 1, 0, "", None),
    ("fuel_info_led",            2, 4, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("stop_start_led",           2, 6, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("artiv_led",                3, 0, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("preconditioning",          3, 3, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("ac_recycling",             3, 4, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("overspeed_led",            3, 6, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
    ("stt_led",                  4, 6, 2, 1, 0, "", {0: "off", 1: "on", 2: "blink"}),
]

CAN_DEFINITIONS[0x217] = [
    ("airbag_disabled",         0, 0, 2, 1, 0, "", None),
    ("black_panel",             0, 3, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("brightness",              0, 4, 4, 1, 0, "", None),
    ("distance_unit",           1, 0, 1, 1, 0, "", {0: "km", 1: "miles"}),
    ("cmb_fault",               1, 3, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("auto_check",              1, 4, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("check_active",            1, 5, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("airbag_fault",            1, 6, 2, 1, 0, "", {0: "ok", 1: "fault"}),
    ("rheostat_minus",          2, 0, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("rheostat_plus",           2, 1, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("sport_pushed",            2, 4, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("child_lock_pushed",       2, 5, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("esp_pushed",              2, 6, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("aas_pushed",              2, 7, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("rear_window_heating_pushed", 3, 4, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("ac_on_pushed",            3, 5, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("overspeed_pushed",        3, 7, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("stop_and_go_engine_stop", 4, 7, 1, 1, 0, "", {0: "off", 1: "stopped"}),
    ("speed_displayed_on_cmb",  5, 0, 8, 1, 0, "km/h", None),
    ("alert_level_0",           6, 7, 1, 1, 0, "", {0: "disabled", 1: "enabled"}),
    ("alert_level_1",           6, 6, 1, 1, 0, "", {0: "disabled", 1: "enabled"}),
    ("alert_level_2",           6, 5, 1, 1, 0, "", {0: "disabled", 1: "enabled"}),
    ("alert_level_3",           6, 4, 1, 1, 0, "", {0: "disabled", 1: "enabled"}),
    ("alert_level_8",           7, 7, 1, 1, 0, "", {0: "disabled", 1: "enabled"}),
    ("alert_level_9",           7, 6, 1, 1, 0, "", {0: "disabled", 1: "enabled"}),
    ("alert_level_15",          7, 0, 1, 1, 0, "", {0: "disabled", 1: "enabled"}),
]

CAN_DEFINITIONS[0x126] = [
    ("space_measure_request", 0, 0, 1, 1, 0, "", {0: "off", 1: "requested"}),
    ("hook_present",          0, 1, 1, 1, 0, "", {0: "no", 1: "yes"}),
    ("trailer_present",       0, 2, 1, 1, 0, "", {0: "no", 1: "yes"}),
    ("disable_visual",        0, 3, 1, 1, 0, "", {0: "enabled", 1: "disabled"}),
    ("disable_sound",         0, 4, 1, 1, 0, "", {0: "enabled", 1: "disabled"}),
    ("gearbox_selection",     1, 4, 4, 1, 0, "", {0: "BVA", 1: "BVM", 2: "BVMP"}),
]

CAN_DEFINITIONS[0x297] = [
    ("mirror_manual_movement", 0, 0, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("memo_recall",            0, 1, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("memorize",               0, 2, 1, 1, 0, "", {0: "off", 1: "active"}),
    ("vth_active",             0, 3, 2, 1, 0, "", {0: "inactive", 1: "active", 2: "unavailable"}),
    ("display_fault",          0, 5, 1, 1, 0, "", {0: "ok", 1: "fault"}),
    ("speed_kmh",              1, 0, 8, 1, 0, "km/h", None),
]

# ---------------------------------------------------------------------------
# Maintenance & Diagnostics
# ---------------------------------------------------------------------------

CAN_DEFINITIONS[0x3A7] = [
    ("wrench_without_km",          0, 2, 2, 1, 0, "", None),
    ("wrench_with_km",             0, 4, 2, 1, 0, "", None),
    ("maintenance_due",            0, 7, 1, 1, 0, "", {0: "ok", 1: "due"}),
    ("km_blinking",                1, 5, 1, 1, 0, "", {0: "off", 1: "blinking"}),
    ("maintenance_sign_km",        1, 7, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("time_blinking",              2, 5, 1, 1, 0, "", {0: "off", 1: "blinking"}),
    ("maintenance_sign_time",      2, 7, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("maintenance_km",             3, 0, 16, 1, 0, "km", None),
    ("days_before_maintenance",    5, 0, 16, 1, 0, "days", None),
    ("display_duration",           7, 0, 8, 1, 0, "s", None),
]

CAN_DEFINITIONS[0x136] = [
    ("request_urea_display", 0, 1, 1, 1, 0, "", {0: "off", 1: "requested"}),
    ("urea_remaining",       0, 2, 14, 1, 0, "ml", None),
]

CAN_DEFINITIONS[0x127] = [
    ("showroom_mode", 0, 6, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("enable_vth",    0, 7, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("luminosity",    1, 0, 8, 1, 0, "", None),
]

# ---------------------------------------------------------------------------
# Infotainment
# ---------------------------------------------------------------------------

CAN_DEFINITIONS[0x21F] = [
    ("list",            0, 0, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("mode_phone",      0, 1, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("volume_minus",    0, 2, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("volume_plus",     0, 3, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("seek_down",       0, 6, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("seek_up",         0, 7, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("scroll_position", 1, 0, 8, 1, 0, "", None),
    ("list_minus",      2, 3, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("list_plus",       2, 4, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("source",          2, 6, 1, 1, 0, "", {0: "off", 1: "pushed"}),
    ("command_valid",   2, 7, 1, 1, 0, "", {0: "invalid", 1: "valid"}),
]

CAN_DEFINITIONS[0x760] = [
    ("am_waveband",              0, 1, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("cd_changer_usb",           0, 3, 1, 1, 0, "", {0: "off", 1: "enabled"}),
    ("geographic_location",      0, 4, 4, 1, 0, "", None),
    ("amplifier_enabled",        1, 7, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("parking_aid_enabled",      2, 2, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("cd_text",                  2, 3, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("radio_text",               2, 4, 1, 1, 0, "", {0: "off", 1: "on"}),
    ("number_of_aerials",        2, 7, 1, 1, 0, "", {0: "1", 1: "2"}),
    ("aux1_mode",                3, 5, 2, 1, 0, "", None),
    ("aux2_mode",                3, 4, 2, 1, 0, "", None),
    ("rear_parking_beep_volume", 4, 0, 3, 1, 0, "", None),
    ("front_parking_beep_volume", 4, 3, 3, 1, 0, "", None),
]

CAN_DEFINITIONS[0x228] = [
    ("hour",   0, 0, 8, 1, 0, "", None),
    ("minute", 1, 0, 8, 1, 0, "", None),
]

# ---------------------------------------------------------------------------
# Vehicle Configuration
# ---------------------------------------------------------------------------

CAN_DEFINITIONS[0x15B] = [
    ("car_settings_1", 0, 0, 8, 1, 0, "", None),
    ("car_settings_2", 1, 0, 8, 1, 0, "", None),
    ("car_settings_3", 2, 0, 8, 1, 0, "", None),
    ("car_settings_4", 3, 0, 8, 1, 0, "", None),
    ("car_settings_5", 4, 0, 8, 1, 0, "", None),
    ("car_settings_6", 5, 0, 8, 1, 0, "", None),
    ("car_settings_7", 6, 0, 8, 1, 0, "", None),
    ("car_settings_8", 7, 0, 8, 1, 0, "", None),
]

CAN_DEFINITIONS[0x260] = [
    ("car_settings_1", 0, 0, 8, 1, 0, "", None),
    ("car_settings_2", 1, 0, 8, 1, 0, "", None),
    ("car_settings_3", 2, 0, 8, 1, 0, "", None),
    ("car_settings_4", 3, 0, 8, 1, 0, "", None),
    ("car_settings_5", 4, 0, 8, 1, 0, "", None),
    ("car_settings_6", 5, 0, 8, 1, 0, "", None),
    ("car_settings_7", 6, 0, 8, 1, 0, "", None),
    ("car_settings_8", 7, 0, 8, 1, 0, "", None),
]

CAN_DEFINITIONS[0x336] = [
    ("vin_char_0", 0, 0, 8, 1, 0, "", None),
    ("vin_char_1", 1, 0, 8, 1, 0, "", None),
    ("vin_char_2", 2, 0, 8, 1, 0, "", None),
]

CAN_DEFINITIONS[0x2B6] = [
    ("vin_char_9",  0, 0, 8, 1, 0, "", None),
    ("vin_char_10", 1, 0, 8, 1, 0, "", None),
    ("vin_char_11", 2, 0, 8, 1, 0, "", None),
    ("vin_char_12", 3, 0, 8, 1, 0, "", None),
    ("vin_char_13", 4, 0, 8, 1, 0, "", None),
    ("vin_char_14", 5, 0, 8, 1, 0, "", None),
    ("vin_char_15", 6, 0, 8, 1, 0, "", None),
    ("vin_char_16", 7, 0, 8, 1, 0, "", None),
]

CAN_DEFINITIONS[0x3B6] = [
    ("vin_char_3", 0, 0, 8, 1, 0, "", None),
    ("vin_char_4", 1, 0, 8, 1, 0, "", None),
    ("vin_char_5", 2, 0, 8, 1, 0, "", None),
    ("vin_char_6", 3, 0, 8, 1, 0, "", None),
    ("vin_char_7", 4, 0, 8, 1, 0, "", None),
    ("vin_char_8", 5, 0, 8, 1, 0, "", None),
]
