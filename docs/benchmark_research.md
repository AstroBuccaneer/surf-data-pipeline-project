# Benchmark Research Documentation

## Overview
Two world record benchmarks anchor the entire surf scoring system.
One represents the scientific upper bound of wave height and the
other represents the human surfability ceiling.

## Benchmark 1 — Lituya Bay Megatsunami 1958

### The Event
On July 9 1958 at 10:16 PM local time a magnitude 7.8 earthquake
struck along the Fairweather Fault in Southeast Alaska. The seismic
activity triggered a massive rockslide on the northeast wall of
Lituya Bay. Approximately 90 million tons of rock plunged into
the narrow inlet generating a megatsunami.

### The Wave
- Height: 1,720 feet (524 meters)
- Location: Lituya Bay, Alaska
- Cause: Earthquake triggered rockslide
- Classification: Megatsunami
- Surfable: No

### Why It Matters for This Project
Lituya Bay represents the absolute scientific upper bound for
wave height measurement. No wave has ever been recorded higher.
It establishes the theoretical maximum against which all other
waves can be compared. The seismic cause (magnitude 7.8 earthquake)
directly informs the seismic recurrence scoring component —
locations with higher seismic activity have greater potential
for extreme wave generation events.

### Cause Frequency at Our 4 Locations
| Location | Seismic Events (M4.0+) | Max Magnitude |
|---|---|---|
| Huntington Beach | 830 | 7.2 |
| Waikiki | 253 | 6.9 |
| Pensacola Beach | 6 | 5.9 |
| Cocoa Beach | 1 | 4.0 |

Huntington Beach comes closest to Lituya Bay causative conditions
with 830 seismic events and a max magnitude of 7.2.

---

## Benchmark 2 — Nazaré Big Wave Record 2020

### The Event
On October 29 2020 German big wave surfer Sebastian Steudtner
paddled into a wave at Praia do Norte beach in Nazaré Portugal.
The wave was officially measured at 86 feet (26.2 meters) by
the World Surf League setting a new Guinness World Record for
the largest wave ever surfed.

### The Wave
- Height: 86 feet (26.2 meters)
- Location: Nazaré, Portugal
- Surfer: Sebastian Steudtner
- Cause: Nazaré Canyon amplifying Atlantic swells
- Classification: Big wave surfing record
- Surfable: Yes

### The Nazaré Canyon
The key to Nazaré's giant waves is the Nazaré Canyon — an
underwater canyon that extends approximately 170 kilometers
into the Atlantic Ocean reaching depths of 5,000 meters.
When Atlantic swells travel toward the coast the canyon
funnels and focuses the energy creating waves significantly
larger than surrounding areas.

### Why It Matters for This Project
Nazaré represents the human surfability ceiling — the largest
wave a human has ever successfully surfed. It serves as the
primary 100% benchmark for the surf potential score. Every
location's maximum wave height is expressed as a percentage
of the Nazaré record.

### How Our 4 Locations Compare to Nazaré
| Location | Max Wave (m) | Max Wave (ft) | % of Nazaré |
|---|---|---|---|
| Cocoa Beach | 9.74 | 31.96 | 37.18% |
| Pensacola Beach | 9.36 | 30.71 | 35.73% |
| Waikiki | 9.09 | 29.82 | 34.69% |
| Huntington Beach | 6.35 | 20.83 | 24.24% |

No location reaches even 40% of the Nazaré benchmark showing
significant room for extreme wave events during major storm
or seismic activity.

---

## Benchmark Update Policy
- Lituya Bay — permanent, will never change
- Nazaré — monitored for new records via WSL
- Future Phase 3 implementation will auto update Nazaré
  benchmark if a new world record is set using Airflow DAG
  scraping WSL records on a weekly schedule

  