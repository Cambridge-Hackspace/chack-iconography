# Isometric Network Map Iconography Dictionary

A canonical vocabulary for a custom draw.io icon pack. Every icon has a slug (used as the filename and draw.io library name), a glyph description (what the isometric object looks like), and notes on variants or usage. The glyph descriptions are written so they can be turned into image-generation prompts later.

## 1. Global style rules

These apply to every icon so the pack reads as one family.

| Rule | Value |
|---|---|
| Projection | True isometric, 30° axes (draw.io's isometric grid). Right face lit, left face mid, top face brightest. |
| Light source | Upper-left, fixed. Never vary per icon. |
| Footprint | Objects sit on an implied 1×1, 2×1, or 2×2 isometric tile. Declare the footprint in the slug (`-1x1`, `-2x1`). |
| Canvas | Square SVG/PNG with a fully transparent background — no baked-in page colour, tile, or shadow. Object centred, ~8% padding, baseline of the footprint at the same y-position in every icon so they align on the grid. |
| Line work | Thin dark outline (one weight across the pack), no drop shadows baked in; shadows are a separate overlay icon. |
| Colour | Flat fills, three tones per hue (top/right/left). Neutral grey body for hardware; accent colour is reserved for role and state (see §10). |
| Text | No text inside icons. Labels, IPs, and hostnames are draw.io text, not pixels. |
| Sizes | Three tiers: **S** (1×1, endpoints and services), **M** (2×1, network gear, hosts), **L** (2×2, chassis, storage arrays, clusters). |
| Naming | `iso-<category>-<name>[-<variant>][-<footprint>].svg`, e.g. `iso-net-firewall-2x1.svg`, `iso-state-down.svg`. |

## 2. Physical compute (`iso-compute-*`)

| Slug | Glyph | Notes |
|---|---|---|
| `server-1u` | Flat rackmount slab, front bezel with two drive bays and a status LED strip | Building block; stackable. |
| `server-2u` | Same as 1u, twice the height, four bays | |
| `server-tower` | Upright box, front vents, single optical bay | Legacy/SOHO. |
| `server-hypervisor` | 2u server with three translucent stacked slabs floating above it | Distinguishes hosts that run guests from bare metal. Variants: `-bhyve`, `-kvm`, `-vmware` via a small side badge. |
| `blade-chassis` | Wide L-tier enclosure, eight vertical blade slots, some populated | |
| `rack-empty` | Open 42U frame, side rails only | Container for stacking servers. |
| `rack-full` | Closed cabinet with glass door, faint device outlines behind | Use when contents aren't drawn. |
| `mini-pc` | Small square puck with one port face | Edge nodes, thin clients. |
| `sbc` | Bare green board with pin header and SoC | Raspberry-Pi-class devices. |
| `workstation` | Monitor + tower on a desk-less base | |
| `laptop` | Open clamshell | |
| `phone` | Handset, screen on | |
| `tablet` | Slate, screen on | |
| `thin-client` | Monitor with a puck beneath | |
| `printer` | MFP box with paper tray | |
| `iot-sensor` | Small box with antenna nub and a single blinking LED | |
| `camera` | Bullet camera on a bracket | |
| `bmc` | Small chip with a heartbeat trace | Overlay on a server to show out-of-band management. |
| `console-server` | 1u slab with a row of serial ports | |
| `kvm` | 1u slab with a mini keyboard/monitor icon on the face | |
| `ups` | Tall box with battery glyph on the face | |
| `pdu` | Vertical strip with outlets | |

## 3. Virtual workloads (`iso-virt-*`)

Rendered as translucent or lighter-weight objects so they read as "inside" a host.

| Slug | Glyph | Notes |
|---|---|---|
| `vm` | Translucent cube with a small monitor glyph on the top face | |
| `container` | Shipping-container box, corrugated sides | Docker/Podman. |
| `jail` | Cube with bars on the front face | FreeBSD jails. |
| `pod` | Two or three small containers on one flat pallet | Kubernetes pod. |
| `k8s-cluster` | Hexagonal platform with a ship's-wheel glyph, three pods on it | |
| `function` | Small lightning-bolt tile | Serverless/FaaS. |
| `vswitch` | Flat translucent slab with several port stubs | Software bridge inside a host. |
| `vnic` | Small translucent card | Attach point for guest links. |
| `boot-env` | Cube with a snapshot/clock glyph | ZFS BEs, rollback anchors. |
| `image` | Stacked flat discs (layers) | Container/VM image. |
| `template` | Dashed-outline cube | Golden image / clone source. |

## 4. Services (`iso-svc-*`)

Small S-tier tiles; drop onto a host or VM, or use standalone for logical diagrams.

| Slug | Glyph |
|---|---|
| `web` | Globe on a tile |
| `app` | Gear on a tile |
| `api` | Two plugs connecting |
| `database` | Cylinder |
| `database-replica` | Cylinder with a mirror-arrow |
| `cache` | Cylinder with a lightning bolt |
| `queue` | Row of envelopes on a conveyor |
| `object-store` | Bucket |
| `file-share` | Folder with a network tail |
| `dns` | Signpost |
| `dhcp` | Ticket dispenser |
| `ntp` | Clock face |
| `mail` | Envelope |
| `ldap` / `idp` | Address book with a key |
| `ca` | Rosette/seal with a ribbon |
| `secrets` | Vault door |
| `proxy` | Two-way arrow through a wall slot |
| `reverse-proxy` | Funnel |
| `load-balancer` | Splitter fan (one in, three out) |
| `monitoring` | Heartbeat line on a screen |
| `logging` | Scroll |
| `metrics` | Bar chart |
| `backup` | Archive box with a clock |
| `ci-runner` | Robot arm |
| `registry` | Warehouse shelf with images |
| `git` | Branching node graph |
| `chat` | Speech bubble |
| `game-server` | Gamepad |
| `voice` | Headset |
| `dispatcher` | Traffic-controller paddle |
| `scheduler` | Calendar with a checkmark |
| `generic` | Blank tile with a question mark — placeholder |

## 5. Network devices (`iso-net-*`)

| Slug | Glyph | Notes |
|---|---|---|
| `switch-l2` | 1u slab, full row of RJ45 ports, no status screen | |
| `switch-l3` | Same, with a small routing-arrows badge on the face | |
| `switch-core` | 2u chassis, two port rows, dual PSU | |
| `switch-poe` | L2 switch with a lightning badge | |
| `router` | Round-cornered puck with four outward arrows on top | Classic Cisco-style silhouette, isometric. |
| `router-edge` | Router with a globe badge | Internet-facing. |
| `firewall` | Brick wall segment with a flame at the top | Use for OPNsense/pf/hardware. |
| `firewall-vm` | Translucent brick wall | Virtualised firewall. |
| `utm` | Firewall with a shield badge | |
| `ids-ips` | Radar dish on a slab | |
| `vpn-gateway` | Slab with a tunnel-mouth glyph | |
| `wireless-ap` | Flat disc with three radiating arcs | |
| `wireless-controller` | 1u slab with an antenna badge | |
| `modem-ont` | Small box with a fibre pigtail | |
| `load-balancer-hw` | 1u slab with a splitter fan badge | |
| `proxy-appliance` | 1u slab with a funnel badge | |
| `patch-panel` | 1u slab, port row, cable stubs coming out | |
| `media-converter` | Tiny box, copper on one side, fibre on the other | |
| `sfp` | Small transceiver | Overlay on a port. |
| `tap` | Small inline box with a side arrow | Packet tap/SPAN. |
| `cell-gateway` | Box with a cellular antenna | 4G/5G backup. |

## 6. Storage (`iso-stor-*`)

| Slug | Glyph | Notes |
|---|---|---|
| `disk` | Single 3.5" drive | |
| `ssd` | Slim 2.5" drive | |
| `nvme` | Stick with chips | |
| `nas` | Desktop box with 4–8 vertical drive slots | |
| `san` | 2u array, two controllers, many bays | |
| `jbod` / `disk-shelf` | Wide L-tier shelf, front-loaded drives, no controller | |
| `zfs-pool` | Flat platform holding several disk stacks under a translucent dome | Variants: `-mirror`, `-raidz` via a badge. |
| `zfs-dataset` | Small tray on a pool | |
| `snapshot` | Disc with a camera glyph | |
| `distributed-fs` | Three small disk stacks joined by dotted links on a shared platform | Gluster/Ceph/MooseFS. |
| `object-bucket` | Bucket (larger than the service tile) | |
| `tape-library` | Cabinet with a robot arm and cartridges | |
| `backup-target` | Vault box with an archive badge | |
| `replication` | Two disk stacks with a curved arrow between | |

## 7. Cloud and external (`iso-ext-*`)

| Slug | Glyph | Notes |
|---|---|---|
| `internet` | Large cloud, globe embossed | |
| `cloud-generic` | Plain cloud | |
| `cloud-provider` | Cloud with a blank badge slot | Add provider mark as draw.io text/logo, not baked in. |
| `saas` | Cloud with a gear | |
| `cdn` | Cloud with radiating nodes | |
| `isp` | Cloud with a router inside | |
| `remote-site` | Small building | |
| `datacenter` | Large building with rooftop HVAC | |
| `home-site` | House | |
| `colo-cage` | Fenced square platform | |
| `mobile-network` | Cell tower | |
| `satellite` | Dish on a mast | |

## 8. Boundaries and zones (`iso-zone-*`)

Flat isometric tiles or translucent boxes that other icons sit on or in. Should scale freely.

| Slug | Glyph |
|---|---|
| `site` | Large flat tile, thick border |
| `rack-row` | Long thin tile |
| `vlan` | Flat tile, coloured border, dashed inner line |
| `subnet` | Flat tile, solid border |
| `dmz` | Flat tile with hazard-stripe border |
| `trust-high` | Tile with a green border |
| `trust-low` | Tile with a red border |
| `management` | Tile with a wrench badge in the corner |
| `cluster` | Translucent box enclosing multiple hosts |
| `vpc` | Cloud-textured tile |
| `availability-zone` | Tile with a compass badge |
| `tenant` | Tile with a person badge |
| `air-gap` | Tile with a broken-link border |

## 9. Links (`iso-link-*`)

Links are draw.io edge styles rather than raster icons, but define them here so the legend and any connector end-cap icons match.

| Slug | Style | Notes |
|---|---|---|
| `copper` | Solid, medium weight, neutral | Ethernet 1G. |
| `copper-10g` | Solid, heavy | |
| `fibre` | Solid, orange/yellow | |
| `fibre-100g` | Solid, heavy, orange | |
| `wireless` | Dashed arcs, no line | |
| `wan` | Solid, blue, heavy | |
| `internet-uplink` | Solid, blue, arrowhead at cloud | |
| `vpn-tunnel` | Double line (pipe), dashed centre | WireGuard/IPsec. Badge with `iso-badge-lock`. |
| `lag-trunk` | Two parallel solid lines | Also for VLAN trunks; annotate with tag list. |
| `replication` | Dotted, purple, arrow | ZFS send, DB replicas. |
| `heartbeat` | Dotted, red, both arrows | Cluster/failover. |
| `management-oob` | Dash-dot, grey | IPMI/console. |
| `serial-console` | Dash-dot, thin grey | |
| `virtual` | Thin translucent | Guest ↔ vswitch. |
| `redundant` | Two lines with a small "2" badge | |
| `planned` | Any style, light grey, dashed | Future work. |
| `blocked` | Any style with a red ✕ badge midpoint | Denied path. |

End-cap icons: `iso-link-endcap-port` (small port block), `iso-link-endcap-sfp`, `iso-link-endcap-antenna`.

## 10. State overlays (`iso-state-*`)

Small badges anchored to the top-right corner of any object icon. Colour is the primary signal; shape is the secondary signal for colour-blind readers.

| Slug | Colour | Shape |
|---|---|---|
| `up` | Green | Filled circle |
| `degraded` | Amber | Triangle |
| `down` | Red | Octagon / ✕ |
| `unknown` | Grey | Hollow circle with ? |
| `maintenance` | Blue | Wrench |
| `primary` | Gold | Star |
| `replica` / `standby` | Silver | Hollow star |
| `active` | Green | Play glyph |
| `passive` | Grey | Pause glyph |
| `planned` | Light grey | Dashed outline of the parent |
| `decommissioned` | Grey | Strikethrough band |
| `rollback-anchor` | Purple | Anchor |

## 11. Security and annotation badges (`iso-badge-*`)

| Slug | Glyph |
|---|---|
| `lock` | Padlock |
| `key` | Key |
| `cert` | Certificate ribbon |
| `shield` | Shield |
| `alert` | Exclamation triangle |
| `quarantine` | Biohazard trefoil |
| `encrypted-at-rest` | Padlock on a disk |
| `public` | Open eye |
| `private` | Crossed-out eye |
| `wrench` | Wrench (management) |
| `clock` | Clock (scheduled) |
| `number-1..9` | Numbered discs for legend callouts |
| `ip-tag` | Small blank label plate for draw.io text |
| `pin` | Map pin (point of interest) |

## 12. People and actors (`iso-actor-*`)

| Slug | Glyph |
|---|---|
| `user` | Neutral figure |
| `admin` | Figure with a wrench |
| `developer` | Figure with a laptop |
| `attacker` | Figure with a hood, red accent |
| `service-account` | Robot |
| `group` | Three figures |
| `agent` | Robot with a cursor | 

## 13. Legend and chrome (`iso-legend-*`)

| Slug | Glyph |
|---|---|
| `legend-plate` | Flat rectangular tile with a title bar |
| `scale-tile` | One reference isometric tile |
| `compass` | Isometric north arrow |
| `title-plate` | Wide flat plate for the diagram title |
| `shadow` | Soft ellipse, used under any object |
| `spacer` | Empty transparent tile for layout |

## 14. Recommended draw.io library layout

Icons are generated programmatically (see `iso/` and `build.py` in this repository), not drawn by hand or by an image model. The dictionary is the source of truth; the generator consumes it, and a test asserts the two stay in sync.

Ship one `.xml` library per category (`iso-compute.xml`, `iso-net.xml`, …) plus a combined `iso-all.xml`. Set every shape's `aspect=fixed`, snap-to-grid on, and grid size to the isometric tile width so M and L icons align automatically. Keep link styles in a separate `iso-links.xml` as edge presets.

## 15. Minimum viable pack

If generating everything at once is too much, this subset covers most topology diagrams:

`server-1u`, `server-hypervisor`, `vm`, `jail`, `container`, `switch-l2`, `switch-l3`, `router`, `firewall`, `wireless-ap`, `nas`, `zfs-pool`, `distributed-fs`, `internet`, `remote-site`, `zone-vlan`, `zone-dmz`, `zone-cluster`, all of §10 states, `badge-lock`, `actor-user`, `actor-admin`, `legend-plate`, `shadow`.

## 16. Theme: Cambridge Hackspace

Modelled on cambridgehackspace.com — a light ground, `#333` structural
rules, and the four-circle brand mark in red, blue, gold and green. Unlike a
monochrome hardware pack, chack wears the brand *on the objects*: the icon
bodies are coloured by domain, so a diagram reads its shape of the world in
the brand's own colours. The icon pack should feel like a diagram that
belongs on that site.

### Domain colours

Every object that draws an isometric body takes a brand hue from its
category. Its three faces (top lit, then right, then left, shadowed) and its
outline are shades of that one hue — a warm, friendly line-art look rather
than grey boxes:

| Hue | Base | Domains |
|---|---|---|
| blue | `#3d84af` | compute, services, cloud-native (`compute`, `svc`, `k8s`, `virt`, `ext`) |
| green | `#89b108` | storage & physical plant (`stor`, `facility`, `edge`, `endpoint`) |
| gold | `#d8a300` | network & connectivity (`net`, `link`) |
| red | `#c34e4b` | security (`sec`) — tints of red, never the pure alarm hex |

People (`actor`) and annotation layers (`badge`, `state`, `legend`,
`chrome`) stay neutral warm-grey, so the colour carries meaning. Security
bodies wear *tints* of red; the pure alarm red (`accent`, below) stays
reserved, so a real fault still pops against them.

### Palette

The four brand colours were sampled from the site's own logo and index
images on 2026-09-05: red `#c34e4b`, blue `#3d84af`, gold `#d8a300`, green
`#89b108`; the structural grey `#333` is from the site CSS. The pack ships
light-forward (the site's footing) but keeps a dark variant. Below is the
neutral base (grounds, ink, accent, states, links); the per-category body
faces and outline override the neutral `body-*`/`outline` shown here.

| Token | Hex (dark) | Use |
|---|---|---|
| `bg-canvas` | `#1b1c1e` | Diagram background (draw.io page colour). Neutral charcoal, not pure black, so outlines still separate. Light: `#ffffff`. |
| `bg-zone` | `#242629` | Zone/site tiles. One step up from canvas. |
| `bg-zone-alt` | `#2e3034` | Nested zone (VLAN inside subnet inside site). Each nesting level steps up one shade. |
| `body-top` | `#4b4b48` | Top face — neutral fallback; per-category hue tints override. |
| `body-right` | `#3a3a37` | Right (lit) face. Neutral fallback. |
| `body-left` | `#2c2c29` | Left (shadow) face. Neutral fallback. |
| `outline` | `#6c6c68` | Edge lines — neutral fallback; per-category a saturated shade of the domain hue. Light neutral: `#3a3a38`. |
| `ink` | `#ececee` | Labels, legend text, port glyphs. Light: `#26282b`. |
| `ink-muted` | `#a7a9ad` | Secondary labels: IPs, VLAN tags, footnotes. Light: `#5c5e62`. |
| `accent` | `#c34e4b` | The brand red. Reserved — see rules below. |
| `accent-dim` | `#8f3634` | Red at rest (unlit badge, planned-but-critical). |
| `virt` | `#ececee` @ 18% alpha | Translucent fill for VMs, jails, containers, vswitches. Inverts with `ink` in the light variant. |

State colours from §10 stay semantic, drawn from the three non-reserved
brand colours (green up, gold degraded, blue maintenance) with red for down:

| State | Hex |
|---|---|
| up | `#89b108` |
| degraded | `#d8a300` |
| down | `accent` (`#c34e4b`) |
| maintenance | `#3d84af` |
| primary | `#c9a227` |
| unknown / standby | `ink-muted` |

Link colours: copper `ink-muted`, fibre `#d8a300`, WAN/internet `#3d84af`, VPN `#7a5bc4`, replication `#9b6fd6`, heartbeat `accent`, management `outline` dash-dot.

### Rules for the accent

The site uses red exactly once per viewport. The pack should do the same.

- Red means **attention**: `state-down`, `badge-alert`, `actor-attacker`, `link-blocked`, `heartbeat`, and the neuron mark itself.
- Nothing decorative is red. No red highlights on switch faces, no red LEDs for "on". Powered-on LEDs are `ink` at low alpha.
- A healthy diagram should contain no red at all. If a reader sees red, something is wrong or someone is hostile.
- `firewall` is the one hardware exception: the flame glyph on the wall may use `accent-dim`, never full `accent`, so it reads as "this is a firewall" rather than "this firewall is down".
- `zone-trust-low`'s border is `accent-dim`, not `accent`, for the same reason: a low-trust boundary is a standing fact about the network, not an alarm, and a healthy diagram that contains one should still contain no full red.

### Transparency

Every icon ships with a transparent background so it works on the dark canvas, the light variant, and any zone tile without a halo.

- No background colour, plate, or shadow is ever baked into an object icon. `bg-canvas` and `bg-zone*` are draw.io page and shape fills, not pixels in the pack.
- Zones (§8) are draw.io shapes with alpha fills, not raster icons, so they tint whatever sits behind them.
- Translucent objects (§3 `virt`, `legend-shadow`) use real alpha — SVG `fill-opacity` or an 8-bit PNG alpha channel — not a pre-blended grey.
- The `outline` tone is chosen to read on both grounds; `ink` glyphs on faces are opaque so they don't wash out on light backgrounds.
- Image generators won't produce true alpha. Generate each icon on a flat, out-of-palette chroma key (e.g. `#00FF00` or `#FF00FF`), key it out, then vectorise (or keep as PNG-32). Never generate on black or white — the anti-aliased edge fringe will show on the other ground.

### Surface treatment

- Matte. No gradients, no specular highlights, no bevels. Three flat tones per object, full stop.
- Outlines are a single weight, lighter than the faces (`outline`), so objects separate from `bg-canvas` without a glow.
- Shadows (`legend-shadow`) are `#000000` at 35% alpha, a flat ellipse, no blur.
- Translucent virtual objects show the host's face lines through them — that's the cue that they're inside something.
- Glyphs on faces (badges, port rows, drive bays) are `ink` or `ink-muted`; no colour except for state badges.

### Typography (draw.io labels)

- Face: the site's own display face — **Jost** (fallbacks Futura, Century Gothic, sans-serif, per the site CSS). One family, two weights.
- Hostnames: `ink`, regular, sentence case, under the object.
- Roles/sections: `ink-muted`, small caps or uppercase with tracking, above zones — mirroring the site's `01 — Consulting` section markers. Number zones the same way: `01 — Edge`, `02 — Hypervisors`, `03 — Storage`.
- IPs, VLAN IDs, ports: `ink-muted`, monospace — **IBM Plex Mono**, the site's own mono face — smaller.
- Dashes are en-dashes with spaces (`—` as the site uses), never hyphens standing in for them.

### Composition

- Left-to-right or top-left-to-bottom-right flow: internet/edge upper-left, storage lower-right, matching the site's reading order.
- Generous negative space. Zones should have at least one empty tile of margin around their contents.
- Legend is a `legend-plate` in the lower-right, same tone as `bg-zone`, titled `Legend` in the muted role style.
- Title plate upper-left: diagram name in `ink`, subtitle (date, revision, author) in `ink-muted`.
- The neuron mark, if used, goes once in the title plate at small size and nowhere else.

### Light mode variant

For print or docs on a white page, invert the greys only: `bg-canvas` → `#ffffff`, zones → `#f6f5f2` / `#eeede8`, body faces → `#e2e0dc` / `#d0cec8` / `#bebcb4`, outline → `#42403a`, ink → `#111110`, ink-muted → `#5a584f` (the dark family's warm tint, mirrored). Accent and state colours stay identical. `ink` on translucent virtual objects must also invert, or the glyphs vanish on white (confirmed in the proof of concept). Both variants are generated from the same slug; the light build lands in `dist/svg-light/` under the same filename.
