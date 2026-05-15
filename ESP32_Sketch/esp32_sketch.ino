#include "driver/twai.h"

#define TX_PIN GPIO_NUM_5
#define RX_PIN GPIO_NUM_4

// Binary packet: [id_hi, id_lo, dlen, data0..data7]
// Max 11 bytes per frame
static uint8_t packet[11];

void setup() {
  Serial.begin(115200);
  while (!Serial);

  twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(TX_PIN, RX_PIN, TWAI_MODE_LISTEN_ONLY);
  twai_timing_config_t t_config = TWAI_TIMING_CONFIG_125KBITS();
  twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

  twai_driver_install(&g_config, &t_config, &f_config);
  twai_start();
}

void loop() {
  twai_message_t rx_msg;

  if (twai_receive(&rx_msg, pdMS_TO_TICKS(10)) == ESP_OK) {
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
