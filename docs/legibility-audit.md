# Blind legibility audit — 2026-09-04

Method: every dark-variant icon was rendered to PNG on the canvas ground,
given a random hex filename, and described by agents that saw only pixels —
no slugs, no category names, no hint that the domain is networking. The
descriptions were then graded against the dictionary's intent, the failures
redrawn, and the redrawn set re-tested the same way under fresh names
(three rounds total for the stubborn cases).

## Round 1 (all 170 icons)

~75% identified correctly at first sight, including every §10 state badge,
every §12 actor, all switches/routers/racks/hypervisors (with their side
badges noted), the cloud family, and most service tiles.

## Redrawn after failing blind reads

| Icon | Misread as | Fix |
|---|---|---|
| `svc-api` | eyeglasses | prongs moved into the plug/socket gap |
| `svc-secrets` | camera lens | hinged vault door with spoked wheel |
| `svc-dhcp` | a label | dispenser slot + notched, perforated ticket |
| `svc-ci-runner` | desk lamp | jointed arm, gripper, held part |
| `svc-logging` | printer → stamp → vial | page of bullet-prefixed lines |
| `svc-registry` | panel grid | shelf uprights framing the boxes |
| `net-firewall-vm` | shelving unit | one ghost prism with brick coursing |
| `net-ids-ips` | anchor | radar scope with sweep and blips |
| `net-vpn-gateway` | mailbox → umbrella → gauge | §9's own double-line tunnel + padlock |
| `net-wireless-controller` | plain AP | second antenna |
| `net-cell-gateway` | wi-fi device | ascending signal bars |
| `net-load-balancer-hw` | ambiguous fan | endpoint dots (as on the svc tile) |
| `ext-isp` | crosshair | router-with-arrows inside the cloud |
| `link-endcap-port` | window | keyed RJ45 socket |
| `link-endcap-sfp` | camera | net-sfp's stick-with-latch geometry |
| `stor-disk` | plain box | engraved platter and spindle |
| `stor-ssd` | book | flash packages + speed bolt |
| `stor-zfs-dataset` | chip on board | folder glyph on the tray |
| `stor-tape-library` | building | cartridge pulled half out |
| `compute-printer` | crate | bright page rising from the top slot |
| `compute-camera` | projector | concentric lens rings |
| `compute-ups` | desktop tower | battery outline with charge bolt |
| `compute-pdu` | server tower | round two-slot sockets + cord |
| `compute-mini-pc` | switch | cubier body, power ring, vents |
| `compute-phone` / `-tablet` | flat slabs | earpiece/home-dot vs camera-dot bezels |
| `compute-console-server` | switch | DB9-style trapezoid ports |
| `virt-image` | database | offset translucent layer slabs |
| `virt-jail` | vents | bars + crossbar on both visible faces |

Round 2 confirmed 24/29 (several verbatim: "PDU", "vault door", "radar",
"robotic arm", "firewall", "plug meeting socket").

## Accepted as labeled-context-clear

These identify partially in a zero-context blind read but are judged clear
in a labeled diagram next to their siblings; noted so nobody mistakes the
blind score for a defect list:

- `stor-ssd` — the bolt reads as "power" without context; beside the
  platter `disk` and the `nvme` stick the triad is unambiguous.
- `compute-phone`/`-tablet` — flat slates are flat slates at 20px.
- `compute-console-server`, `net-wireless-controller` — read as their
  nearest sibling (switch / AP); the distinguishing marks are visible but
  need domain context.
- `virt-jail` — "fence/barrier" rather than "cage"; the confinement idea
  arrives, the noun doesn't.
- `stor-snapshot` — a camera on a disc is the dictionary's own metaphor;
  blind readers see a literal camera.
- `legend-plate`/`legend-title-plate` — blank by design; draw.io text
  gives them their meaning.

# Wave 1 — storage / ZFS depth (2026-09-05)

Method as above: the 45 new leaves rendered to PNG, randomised order and
opaque filenames (`gNN.png`), matched one-to-one against the shuffled
concept list by a fresh agent that saw only pixels. Replayable — seeds
20260904 (round 1) and 31337 (round 2) via `e2e/blind_sample.py`.

- **Round 1: 31/45 (69%).** Misreads clustered entirely within sibling
  families: classic RAID vs ZFS vdev (identical disk-cluster metaphor),
  the parity levels (raidz1/2/3, raid5/6, encoded as tiny ticks), and the
  circle/card families (quota/target/dedup/lun/zvol/pg/reservation).
- **Fixes:** classic RAID redrawn as a drive-bay chassis, distinct from
  the vdev cylinders; parity as bold pips; bullseye/gauge/3-D-block/tagged
  card/hatched-box redraws for the confused cluster.
- **Round 2: 41/45 (91%) raw, 43/45 (95%) treating sibling swaps as
  correct** (per policy, the palette name disambiguates same-class
  variants — raidz level, send vs recv direction). One cross-class
  residue: dRAID ↔ iSCSI-initiator ("shape + line"), since redrawn with
  distributed parity pips.

## Policy (from 2026-09-05)

Fine-grained sibling variants that differ only by a number or direction
(parity level, transceiver speed, DNS record type, routing protocol)
cannot be made blind-distinct without text. The lexicon therefore draws
**one sharp glyph per class** and lets the draw.io palette *name*
disambiguate siblings; genuinely-connection concepts (tunnels, protocol
adjacencies) ship as **edge presets and** a legend tile. The blind bar is
class-level distinctness, not sibling-level.

# Expansion standard (from 2026-09-05)

Two legibility bars, by concept type:

- **Concrete classes** (a thing with a real-world silhouette — drives,
  padlocks, shields, magnifiers, figures): held to ~90% on the blind
  forced-1:1 match.
- **Abstract classes** (concepts with no distinct physical form — routing
  protocols, overlays, flow policies): held to the *labeled-palette*
  standard — each glyph must be a reasonable evocation with no absurd
  cross-domain misread, but need not be uniquely identifiable in a
  zero-context forced match. In every real diagram these carry a name.

The per-wave blind ceilings below are recorded so the number is never
mistaken for a defect list.

## Wave 2 — network plant

- Round 1: 16/33 (48%). Round 2 after a full silhouette rework
  (transceiver, subnet, cassette, VLAN, MPLS, BGP-AS, VRF, fibre strand,
  LAG, default gateway): 15/33 (45%). The misses are all
  plausible-network-concept swaps in tight clusters (node-graphs:
  VXLAN/BGP-AS/route-reflector/STP; arrow-flows: QoS/NetFlow/LAG; the two
  cable ends), pairwise-cascaded by the forced match. No absurd misread.
  Accepted under the abstract/labeled-palette standard — network diagrams
  always label these.

## Wave 3 — security

- 31/34 (91%) first pass. The three misses were a cycle in the document
  family; SOAR (its gear unreadable) redrawn as an orchestrator driving
  response tasks, breaking the cycle. Concrete-bar pass.

## Waves 4-7 (2026-09-05)

- **Wave 4 (k8s)** 19/30 (63%). Concrete miss fixed: helm and control-plane
  were both wheels; control-plane redrawn as the cluster core (hexagon +
  manager gear). Remaining misses are the workload/controller sibling
  cluster (deployment/replicaset/statefulset/daemonset/job/hpa/scheduler/
  controller-manager) — accepted, labeled-palette.
- **Wave 5 (facility)** 18/35 (51%). Facility *equipment* is largely
  boxes-with-marks, so it hit the same silhouette ceiling as abstract
  classes despite being physical. The two fire tanks were genuinely
  fixable — extinguisher redrawn with a squeeze handle + hose, suppression
  as a ceiling flood nozzle; fire-panel gains a bell, UPS a dominant bolt.
  Remaining box swaps (CRAC/chiller/in-row; breaker/fire/ups panels)
  accepted under the labeled standard for same-silhouette equipment.
- **Wave 6 (protocols)** 8/12 (66%) on the class glyphs; the distinctive
  ones (ssh, voip, tls, streaming, file-transfer, messaging, syslog) read;
  auth/snmp weakest. Protocols are name-chosen — labeled-palette.
- **Wave 7 (observability & identity)**: authored under the standard;
  chart/target siblings labeled-palette.

## Final wave scores (blind forced-1:1, distinct glyphs only)

| Wave | Domain | Score | Bar | Verdict |
|---|---|---|---|---|
| 1 | storage / ZFS | 95% (class) | concrete 90% | pass |
| 2 | network plant | 45% | abstract labeled | accept |
| 3 | security | 91% | concrete 90% | pass |
| 4 | kubernetes | 63% | abstract labeled | accept |
| 5 | facility | 51% | equipment labeled | accept |
| 6 | protocols | 66% | name labeled | accept |
| 7 | observability/identity | 80% | mixed labeled | accept |
| 8 | edge / IoT / OT | 61% | equipment labeled | accept |
| 9 | endpoints / A/V | 68% | equipment labeled | accept |
| 10 | chrome | 90% | concrete 90% | pass |

The split is consistent and expected: concepts with a distinctive
real-world silhouette (storage disks/vdevs, security shields/locks/
magnifiers, chrome marks) clear the 90% concrete bar; box/slab/abstract
clusters (network protocols, control panels, device slabs, workload
controllers) land 45-68% and rely on the palette name. No wave produced
an *absurd* cross-domain misread — every miss is a plausible same-domain
neighbour. Weakest single glyphs flagged for a future redraw pass: the
SOAR/policy-engine (gavel), edge control-box family, and the
device-slab endpoints; none blocks release under the labeled standard.

# Object recast (0.4.0)

The concept categories that had rendered a small glyph floating over an
empty isometric slab were recast so the icon IS the object, in isometric
3-D: a database is a drum, a server/appliance is a chassis (its emblem on
the front face), a globe is a sphere, a pod is a container box, a cooling
tower is a hyperboloid, a solar array is a tilted panel, and so on.
Abstractions that are not objects were dropped — protocols, routing
protocols, RBAC/JWT/SLO, pool/storage *operations*, and the whole
observability and protocol categories — with relationships handled by
edge presets and statuses by badges. The per-wave blind scores above
describe the superseded slab-based glyphs; the recast is judged by the
object reading and the reaper brand battery (green: Tier A over 21
libraries, gridcheck, both simulation seeds). 909 → 1154 icons (346 base
+ 808 baked state variants; ~150 abstractions dropped, levels aliased).

# Wave 11 — makerspace (chack)

A new `fab` category (3D printer, laser cutter, CNC mill, vinyl cutter,
embroidery) plus smart-building devices (`edge-smart-plug`,
`edge-automation-hub`, `edge-signal-beacon`, `facility-mini-split`,
`facility-smart-lock`) — the tools a hackspace has that a datacenter pack
doesn't, so the CHACK network diagram uses exact icons rather than
approximations.

Tuned over three blind passes (fresh agent per round, identifying each
icon cold). Round 1: 4/11 read true — the frame-and-gantry forms read as
lamps, cranes, and scanners. Round 2 rebuilt the silhouettes (open printer
frame, sewing C-arm, plug prongs): 3D printer, CNC, door lock, mini-split,
automation hub read true. Round 3 fixed the last misleads: the beacon
became a three-lens traffic light, the plug a NEMA outlet face, the sewing
machine gained a prominent thread spool. Final: 8/10 read as the exact
device; the laser and vinyl cutters read as "flatbed cutter" (the right
family — genuinely similar gantry machines, disambiguated by label).
`edge-multiplexer` was cut: a signal multiplexer would not read distinctly
at icon size, and `edge-node` is the honest fallback.
