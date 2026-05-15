// Section groups — no emoji, using 3-letter codes for diagnostic terminal aesthetic
export const SECTIONS = [
  { name: 'Drivetrain',             code: 'DRV', canIds: ['0x0B6','0x0F6','0x128','0x161','0x221','0x261','0x2A1','0x167'] },
  { name: 'Lights',                 code: 'LGT', canIds: ['0x128','0x0F6','0x361'] },
  { name: 'Doors & Body',           code: 'BOD', canIds: ['0x0E8','0x220','0x1A1','0x2E1'] },
  { name: 'Safety & Warnings',      code: 'SFT', canIds: ['0x128','0x0E6','0x168','0x120','0x1A1'] },
  { name: 'Suspension & Steering',  code: 'SUS', canIds: ['0x0E8','0x10B','0x2E1','0x036'] },
  { name: 'Climate',                code: 'CLM', canIds: ['0x1E3','0x0F6'] },
  { name: 'Driver Aids',            code: 'AID', canIds: ['0x0E1','0x1A8','0x227','0x217','0x297','0x361','0x126'] },
  { name: 'Maintenance & Diag',     code: 'MNT', canIds: ['0x3A7','0x136','0x168','0x167','0x036','0x127'] },
  { name: 'Infotainment',           code: 'INF', canIds: ['0x21F','0x760','0x228'] },
  { name: 'Vehicle Config',         code: 'CFG', canIds: ['0x361','0x2E1','0x15B','0x260','0x336','0x2B6','0x3B6'] },
];

// Signal metadata: name -> { unit, canId }
export const SIGNAL_META = {};

import { CAN_SIGNALS } from './can-signal-list.js';

for (const [canId, signals] of Object.entries(CAN_SIGNALS)) {
  for (const [name, , , , , , unit] of signals) {
    SIGNAL_META[`${canId}.${name}`] = { unit: unit || '', canId };
  }
}
