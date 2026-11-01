// cast.js — one signature colour per person, identical in every shot.
export const MINH = { top: 'hoodie', color: '#2fa7a0', head: 'none' };                                  // "you"
export const MINHKID = { ...MINH, kid: true };
export const NAM = { top: 'tshirt', color: '#3a6ea5', head: 'cap', headColor: '#f2c21a' };               // best friend
export const BA = { top: 'dress', color: '#8a5ad6', head: 'bun' };                                      // grandmother
export const BAYOUNG = { top: 'dress', color: '#8a5ad6', head: 'ponytail' };
export const ONG = { top: 'tshirt', color: '#e8e0d0', head: 'none' };
export const HUY = { top: 'suit', color: '#4a4a58', face: 'glasses', head: 'none' };                    // sceptical teacher
export const TU = { top: 'tshirt', color: '#d64a33', head: 'ponytail' };                                // fish seller
export const LAN = { top: 'labcoat', face: 'glasses', head: 'bun' };                                    // doctor
export const ME = { top: 'dress', color: '#3fb950', head: 'ponytail' };                                 // mother
export const MC = { top: 'suit', color: '#c9a227', head: 'none' };                                      // host
export const CAST = [NAM, MINH, BA, TU];
