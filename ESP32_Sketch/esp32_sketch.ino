#include "driver/twai.h"

#define TX_PIN GPIO_NUM_5
#define RX_PIN GPIO_NUM_4

// Binary packet: [id_hi, id_lo, dlen, data0..data7]
// Max 11 bytes per frame
static uint8_t packet[11];

void setup() {
  Serial.begin(115200);
  unsigned long serial_start = millis();
  while (!Serial && (millis() - serial_start < 3000));

  twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(TX_PIN, RX_PIN, TWAI_MODE_LISTEN_ONLY);
  twai_timing_config_t t_config = TWAI_TIMING_CONFIG_125KBITS();
  twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

  esp_err_t ret = twai_driver_install(&g_config, &t_config, &f_config);
  if (ret != ESP_OK) {
    Serial.printf("FATAL: twai_driver_install() failed: %s\n", esp_err_to_name(ret));
    while (1);
  }
  ret = twai_start();
  if (ret != ESP_OK) {
    Serial.printf("FATAL: twai_start() failed: %s\n", esp_err_to_name(ret));
    while (1);
  }
}

void loop() {
  twai_message_t rx_msg;

  if (twai_receive(&rx_msg, pdMS_TO_TICKS(10)) == ESP_OK) {
    if (rx_msg.extd) continue;  // skip extended frames — PSA bus uses only 11-bit IDs

    // Standard 11-bit CAN ID
    packet[0] = (rx_msg.identifier >> 8) & 0xFF;
    packet[1] = rx_msg.identifier & 0xFF;
    packet[2] = rx_msg.data_length_code;

    for (int i = 0; i < rx_msg.data_length_code && i < 8; i++) {
      packet[3 + i] = rx_msg.data[i];
    }

    // Write binary packet to UART
    Serial.write(packet, 3 + rx_msg.data_length_code);
  }
}
