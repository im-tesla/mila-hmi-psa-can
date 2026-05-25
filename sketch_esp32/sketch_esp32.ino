#include "driver/twai.h"

#define TX_PIN GPIO_NUM_5
#define RX_PIN GPIO_NUM_4

// Binary packet: [0xAA, id_hi, id_lo, dlen, data0..data7]
// Sync byte 0xAA is never a valid CAN ID high byte (11-bit IDs top out at 0x07FF).
#define SYNC_BYTE 0xAA
static uint8_t packet[12];

void setup() {
  Serial.begin(115200);
  unsigned long serial_start = millis();
  while (!Serial && (millis() - serial_start < 3000));

  twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(TX_PIN, RX_PIN, TWAI_MODE_NORMAL);
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
  // Serial → CAN transmit: [0xAA, id_hi, id_lo, dlen, data0..data7]
  while (Serial.available() >= 12) {
    if (Serial.peek() != SYNC_BYTE) { Serial.read(); continue; }
    uint8_t buf[12];
    if (Serial.readBytes(buf, 12) < 12) break;
    twai_message_t tx_msg = {};
    tx_msg.identifier = ((uint16_t)buf[1] << 8) | buf[2];
    tx_msg.data_length_code = min((uint8_t)8, buf[3]);
    for (int i = 0; i < tx_msg.data_length_code; i++) tx_msg.data[i] = buf[4 + i];
    twai_transmit(&tx_msg, pdMS_TO_TICKS(10));
  }

  twai_message_t rx_msg;

  if (twai_receive(&rx_msg, pdMS_TO_TICKS(10)) == ESP_OK) {
    if (rx_msg.extd) return;  // skip extended frames — PSA bus uses only 11-bit IDs

    // Standard 11-bit CAN ID
    packet[0] = SYNC_BYTE;
    packet[1] = (rx_msg.identifier >> 8) & 0xFF;
    packet[2] = rx_msg.identifier & 0xFF;
    packet[3] = rx_msg.data_length_code;

    for (int i = 0; i < rx_msg.data_length_code && i < 8; i++) {
      packet[4 + i] = rx_msg.data[i];
    }

    // Write binary packet to UART
    Serial.write(packet, 4 + rx_msg.data_length_code);
  }
}
