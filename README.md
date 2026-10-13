# AMR Replenishment

Code, simulation data, and analysis for **Shielded Rolling-Horizon Optimization for Autonomous Mobile Robot Line-Side Replenishment in Robotic Compact Storage and Retrieval Systems**.

**Author:** Milad Elyasi, Department of Industrial Engineering, Özyeğin University  
**Repository:** https://github.com/miladelyasi/AMR_Replenishment  
**Release:** 1.0.0

The repository contains the simulator, tactical mixed-integer linear programming (MILP) model, reservation-based trajectory admission, dispatch comparators, instance configurations, experiment drivers, and seed-level outputs. All instance data are synthetic. No industrial trace data are included.

## Download and unpack

Download the repository using **Code → Download ZIP**, extract it, and keep the files together. The inner ZIP files contain the source, data, analysis, and experiment source snapshots. From the downloaded repository directory, run:

```bash
python3 unpack.py
```

The script uses the Python standard library, verifies the upload checksums, restores `research_reproduction/`, and verifies every restored file. Allow 2 GiB for the restored material in addition to the downloads. An existing destination is accepted only when its files match the package. To choose a destination, use `python3 unpack.py --output PATH`.

Alternatively:

```bash
git clone https://github.com/miladelyasi/AMR_Replenishment.git
cd AMR_Replenishment
python3 unpack.py
```

To inspect results without running the simulator, begin with `research_reproduction/analysis/episode_summary.csv` and `research_reproduction/analysis/audit_summary.json`. Reading these files does not require Gurobi.

## Directory layout

| Directory or file | Contents |
|---|---|
| `code/` | Simulator, MILP, reservation planner, dispatch policies, configurations, experiment drivers, and execution checks |
| `data/primary/` | 1,215 eight-hour episodes, per-epoch records, and three design manifests |
| `data/technical/` | 65 matched-dispatch and solver-gap episodes, line coverage, and fixed-state solve diagnostics |
| `data/extensions/` | 105 physical-port and dispatch-comparator episodes, with port-service intervals |
| `data/stopping/` | 90 full-episode stopping-policy comparisons, solver gaps, line allocation, timing, and 720 shadow dispatch comparisons |
| `data/accurate_dispatch/` | 30 Absolute MILP episodes and 30 BatchGreedy timing replays at fixed comparator settings |
| `data/joint_stopping/` | 165 executions for complete Absolute screening and fixed cross-preset weights; its analysis also uses 45 stopping-study records |
| `data/learning_selection/` | Recorded seed-4 pair features and MILP selection labels, normalization parameters, and trained checkpoint for the separate offline coverage diagnostic |
| `analysis/` | Episode summaries, paired contrasts, audit summaries, and generated tables and figures; named subdirectories correspond to the experiment groups |
| `analysis/learning/` | Separate service-event learning diagnostics |
| `extension_checks/` | Short functional checks, independently checked tactical decisions, and port-layout checks, excluded from experiment totals |
| `provenance/` | Source snapshots and environment records grouped by experiment design, plus the service-event dataset and learning checkpoints |
| `environment.json` | Experiment hardware, package versions, and source fingerprints |
| `metadata.json` | Dataset scope and execution counts |
| `CITATION.cff` | Citation metadata |
| `MANIFEST_SHA256.txt` | Integrity checksums for the restored files |

## Experiment counts

The schedule-based benchmark comprises **1,700 executions**, including **30 explicitly identified timing replays**.

| Design | Executions | Design details |
|---|---:|---|
| Primary benchmark | 1,215 | 150 screening, 105 objective-weight, 90 nominal interface-capacity, 135 battery, 210 baseline, 495 manufacturing-sensitivity, and 30 travel-relaxed episodes |
| Technical validation | 65 | 60 matched-dispatch episodes on seeds 30–44 and five solver-gap episodes |
| Physical ports and dispatch | 105 | 60 physical-port, 30 BatchGreedy, and 15 UrgencyRank episodes |
| Stopping policies | 90 | Three presets × two stopping policies × 15 seeds |
| Dispatch timing | 60 | 30 Absolute MILP episodes and 30 BatchGreedy timing replays on seeds 30–44 |
| Complete Absolute screening and fixed weights | 165 | 105 screening and 60 fixed-weight episodes; 45 stopping records are reused without counting them again |

Main screening and the five main baselines use 30 seeds; other primary comparisons use 15. The complete Absolute screening analysis has 150 reference-weight observations: five presets with 30 seeds each. Its fixed-weight analysis adds 60 observations at travel weight 2, using four presets and seeds 0–14. Together these analyses use 210 records, of which 165 correspond to new executions and 45 to reused stopping records.

BatchGreedy timing replays repeat the operational outcomes of the corresponding dispatch-comparator episodes. They supply new timing measurements and are not pooled as independent operational observations. Short checks, fixed-state copied solves, shadow decisions, and service-event learning diagnostics are excluded from the 1,700-execution total.

## Set up the simulator

The recorded experiment environment uses Python 3.13.7, Gurobi 13.0.2, an AMD Ryzen 9 9950X3D processor, eight visible logical processors, and approximately 59 GiB of visible memory. MILP episodes use one solver thread each. See `environment.json` for the package versions and source inventories.

From `research_reproduction/code/`:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-pinned.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`. Optimization runs require a Gurobi license suitable for the model sizes; Gurobi licenses are not included in this repository. Learning and visualization dependencies are listed in `pyproject.toml` and `requirements.txt`.

Run one episode:

```bash
python experiments/run_episode.py \
  --config configs/sweep/base__base__k80.yaml \
  --seed 0 --out primary_results/base_k80_MILPOnly_s00.json
```

An episode represents eight simulated hours. For a short functional check, add `--horizon 600`. The output consists of a JSON summary and an adjacent `.epochs.csv` file. Run `python experiments/check_execution.py` for the targeted execution checks.

`run_episode.py` uses `ScheduleSimulator`. The base `world.simulator.Simulator` supports the separate service-event learning model. The two models have different execution semantics; use the specified driver for each study and analyze their outputs separately.

## Reproduce the primary benchmark

From `code/`, run the finite, resumable drivers sequentially:

```bash
python experiments/primary_campaign.py 6
python experiments/additional_campaign.py
python experiments/baseline_campaign.py
```

The first argument controls concurrent episodes in the primary driver. The two other drivers use two workers. They write `code/primary_results/`. Existing episode JSONs are treated as completed runs, so use an empty results directory for a fresh campaign.

Regenerate statistics and figures from the supplied data:

```bash
python experiments/analyze_results.py \
  --results ../data/primary --out ../analysis
python experiments/write_results_discussion.py \
  --analysis ../analysis --out ../analysis/discussion
```

To analyze a fresh campaign, pass `--results primary_results`. The analysis requires complete inputs and verifies identities, mission accounting, battery limits, and execution counters. `--partial` writes a progress summary only. Pointwise percentile-bootstrap intervals use 50,000 resamples. Deterministic contrast-specific streams support reproducible analysis; learning diagnostics use stored bootstrap seeds. Intervals are not adjusted for multiple comparisons. Fresh optimization runs can differ when time limits bind on different hardware or under different concurrent loads.

The tuned-baseline comparison uses seeds 0–14 throughout. Selecting a local weight setting by the lowest observed stockout on those same seeds makes that comparison exploratory.

## Technical, port, and dispatch studies

```bash
python experiments/technical_campaign.py 4
python experiments/analyze_technical.py \
  --primary ../data/primary --validation ../data/technical \
  --out ../analysis/technical

python experiments/extension_campaign.py 4 comparators
python experiments/extension_campaign.py 3 ports
python experiments/analyze_extension.py \
  --primary ../data/primary --technical ../data/technical \
  --extension ../data/extensions --out ../analysis/extensions
```

The campaigns write `technical_results/` and `extension_results/` inside `code/`; substitute these paths to analyze fresh runs. Technical comparator settings are fixed before seeds 30–44: travel weight 2 at preset 80 and reference weights at preset 240. The matched greedy policy uses the same screening, eligibility, and feasibility filters. Solver diagnostics solve copies of eight fixed states per diagnostic episode without changing the running controller.

BatchGreedy checks the same tactical inequalities and carried reservations without an optimizer. Independent fixed-state checks validate its feasibility and objective accounting. Physical-port instances provide two or three distinct delivery access nodes per line; source retrieval remains exclusive. Their results include changes in travel opportunities and port choice as well as service capacity. The physical-port table reuses 30 primary one-port records, and the dispatch comparison reuses 30 technical MILP records; these references are not counted again.

## Stopping-policy and timing studies

```bash
python experiments/stopping_campaign.py 6
python experiments/analyze_stopping.py \
  --results ../data/stopping --out ../analysis/stopping
python experiments/write_stopping_discussion.py \
  --analysis ../analysis/stopping --out ../analysis/stopping/discussion

python experiments/accurate_dispatch_campaign.py 6
python experiments/analyze_accurate_dispatch.py \
  --results ../data/accurate_dispatch --extension ../data/extensions \
  --technical ../data/technical --out ../analysis/accurate_dispatch
python experiments/write_accurate_dispatch_discussion.py \
  --analysis ../analysis/accurate_dispatch --out ../analysis/accurate_dispatch/discussion
```

The drivers write `stopping_results/` and `accurate_dispatch_results/`. The **Reference** stopping policy uses a 0.02 relative gap tolerance and a 150 ms time allowance. **Absolute** retains the objective constant, uses zero relative tolerance, an absolute tolerance of 1e-6 objective-cost units, and a 5 s allowance. The comparison changes both stopping accuracy and time allowance.

The stopping design crosses presets 80, 240, and Broad with both policies on seeds 0–14 at reference weights. Eight fixed target times per episode yield 720 same-state BatchGreedy shadow decisions that do not affect simulation trajectories. The shadow objective advantage concerns the tactical surrogate and does not imply a corresponding episode-level advantage.

The dispatch-timing study uses presets 80/240 and seeds 30–44 with travel weight 2 at preset 80 and reference weights at preset 240. These seeds also occur in the comparator study; this is a matched comparison. Operational and per-epoch outcomes of the 30 BatchGreedy timing replays are checked against the corresponding comparator records.

Controller time includes screening, feasible-alternative construction, and assignment. Complete review latency also includes state construction, trajectory admission, and event bookkeeping. Diagnostic and shadow-comparison time is recorded separately and excluded. Timing comparisons use identical hooks and per-episode aggregates. Concurrent server timings exclude physical sensing and communication and are not hard execution deadlines.

## Complete Absolute screening and fixed weights

Run `python experiments/joint_stopping_campaign.py 6` after the stopping campaign has supplied the 45 Absolute records reused by this design. It writes `joint_stopping_results/` and does not rerun those reused cells.

Regenerate the analysis from the supplied records:

```bash
python experiments/analyze_joint_stopping.py \
  --results ../data/joint_stopping --stopping ../data/stopping \
  --reference ../data/primary --out ../analysis/joint_stopping
```

The manifest specifies all 210 analysis cells, the 165 additional executions, the 45 reused records, objective coefficients, and stopping tolerances. `episodes.csv` identifies reuse explicitly. Screening comparisons use 30 paired seeds at reference weights; fixed-weight comparisons use seeds 0–14 at both weights. These are exploratory matched comparisons. The analysis checks complete raw inputs, battery and execution invariants, and achieved solver gaps before writing estimates. `screening_summary.csv` and `screening_table.tex` report all five presets and both stopping policies on the same 30 seeds, including buffer-accepted and overflow units.

## Learning diagnostics

The manuscript's learning appendix uses a separate service-event simulation model. Its source, output CSVs, and checkpoints are supplied in `provenance/service_event_code/`, `provenance/service_event_results/`, and `provenance/learning_checkpoints.tar.gz`. It is not a learned-controller comparison under `ScheduleSimulator`.

```bash
python experiments/analyze_selection_coverage.py \
  --data ../data/learning_selection --out ../analysis/learning
python experiments/analyze_learning_f1.py \
  --learning-results ../provenance/service_event_results \
  --coverage ../analysis/learning/selection_coverage.csv \
  --out ../analysis/learning
python experiments/analyze_learning_f2.py \
  --learning-results ../provenance/service_event_results \
  --out ../analysis/learning
```

Closed-loop outcomes and paired intervals are regenerated from seed-level records. The offline evaluator loads the recorded seed-4 pair features, original feature normalization, and trained checkpoint from `data/learning_selection/`. Input shards preserve the original JSONL records and their order; its manifest checks their individual hashes and the concatenated source hash. Coverage pools retained selected pairs over all nonempty decision epochs, using the recorded MILP selections as labels. The random comparator uses seed 0. The evaluator writes exact coverage ratios and per-epoch counts; the plot uses the manuscript's three-decimal coverage values. This computation evaluates the supplied checkpoint without retraining. The training pair sets needed to reproduce checkpoint fitting are outside the package's scope. It requires NumPy and PyTorch. The diagnostics do not identify the cause of score collapse or establish learning performance under the schedule-based benchmark.

## Output fields and interpretation

Episode JSONs identify configuration, overrides, method, and random seed. Design manifests define the episode IDs, groups, presets, and policy settings. Preset labels are not counts of robot–job pairs. The benchmark fixes start slot zero for each pair of a currently idle eligible robot and a screened job; alternatives must pass the individual feasibility checks.

| Field | Definition or unit |
|---|---|
| `implementation_version` | Schedule-execution model identifier |
| `stockout_minutes` | Sum of line starvation durations in minutes; an interval begins at unmet consumption and ends at accepted replenishment or the horizon |
| `delivered_total` | Completed delivery missions |
| `accepted_units`, `overflow_units` | Units admitted to finite line buffers or rejected at a full buffer; their sum equals `delivered_total` |
| `total_travel_m` | Complete admitted route distance, booked once at mission admission, in meters |
| `total_energy` | Admitted mission energy in normalized battery units |
| `proposed`, `accepted` | Proposed commitments and admitted missions; admissions include missions active at the horizon |
| `shield_repairs`, `shield_rejections` | Admitted missions with positive start shifts and realization deferrals/rejections |
| `energy_deferrals` | Realized-route energy rejections |
| `eligible_epochs`, `eligible_robot_epochs` | Reviews with eligible idle robots and the summed eligible robot count |
| `mean_idle_rate`, `pooled_idle_rate` | Mean epoch no-proposal fraction and pooled no-proposal fraction over eligible idle robots |
| `accepted_eligible_total` | Admissions intersecting the diagnostic eligible set; when absent in MILP records, it equals `accepted` |
| `mean_admitted_idle_rate`, `pooled_admitted_idle_rate` | Analysis-derived no-admission rates over eligible idle robots |
| `mean_candidate_pairs`, `max_candidate_pairs` | Mean and maximum feasible robot–job alternatives per review; MILP diagnostics |
| `uncovered_robot_epochs` | Eligible robot-epochs lacking retained feasible alternatives |
| `candidate_metrics_applicable` | Marks whether candidate coverage is instrumented; false for heuristic policies |
| `critical_line_fraction` | Line-review observations at or below the safety-stock threshold divided by all line-review observations |
| `min_battery`, `realized_min_battery` | Review-level and admission-inclusive battery minima; the latter checks the battery floor |
| `reservation_node_insert_conflicts` | Failed node-reservation writes when committing a validated plan |
| `reservation_edge_insert_conflicts` | Failed edge-reservation writes when committing a validated plan |
| `planned_drop_time_mismatches` | Completion times differing from admitted times by more than 1e-6 s |
| `missions_past_planned_completion_at_review` | Overdue active missions at review epochs; an execution-stall measure |
| `completed_audited_missions` | Completed missions included in timing checks |
| `planned_drop_time_abs_error_sum`, `planned_drop_time_max_abs_error` | Sum and maximum of absolute completion-time errors in seconds |
| `solver_status_counts` | Counts of solver termination statuses |
| `milp_mean_ms`, `milp_p95_ms`, `milp_max_ms` | Optimization-call timing across reviews, including zero for reviews without a solve; excludes construction and shielding |
| `controller_mean_ms`, `review_mean_ms`, `review_p95_ms`, `review_max_ms` | Controller and complete-review latency summaries in instrumented timing studies |
| `wall_seconds` | Complete episode simulation wall time |

The `.epochs.csv` files record review time, eligibility, proposals, admissions, candidate diagnostics, battery, and critical buffers. Zero-eligible reviews are excluded from epoch-mean idle rates. Busy robots are excluded from these denominators; the rates describe dispatch opportunities, not whole-fleet utilization. Diagnostic eligibility uses battery at least 0.15: a 0.1 admission floor plus a prescribed 0.05 screening reserve. Heuristic proposal rules omit the reserve, and their diagnostics explicitly intersect with the common eligible set.

`.coverage.csv` measures accessible critical lines omitted by screening, with criticality defined by depletion time at most 30 s. `.lines.csv` additionally records each line's screened jobs, feasible alternatives, proposals, admissions, incoming missions, and inventory. Line IDs in raw records are zero-based. `material_balance` and `line_totals` check `initial + accepted - served_consumption - final = 0`.

`.gaps.csv` or `.gaps.json` contains incumbent objectives, bounds, retained constants, achieved gaps, model sizes, and timing. Absolute gap is `abs(objective - bound)`, not an observed decision loss. Fixed-state `changed_assignments` counts the symmetric difference of commitment keys or triple indices, as identified by each study. `.timing.csv` contains controller and review measurements; `.snapshots.json` contains same-state shadow comparisons. In `data/technical/`, use `validation_kind` to distinguish policies; in `data/extensions/`, use `extension_kind`; in `data/accurate_dispatch/`, use `dispatch_policy`. The inherited `method=MILPOnly` field denotes the shared instrumentation shell in these studies.

`.ports.csv` records admitted service intervals by physical delivery node. `port_audit` describes port coordinates, group occupancy, peak per-node occupancy, and simultaneous line service. Time aggregates are clipped to the episode horizon. BatchGreedy's `milp_*_ms` fields contain greedy construction time and its status is `GREEDY`.

Paired contrast direction and sample size are recorded in analysis outputs. An all-zero observed sample produces an all-zero empirical bootstrap interval without establishing zero risk on other realizations. Execution fingerprints in environment records identify the run source; `source_sha256` identifies distributed source files. `MANIFEST_SHA256.txt` verifies the full release.

## Modeling scope

Active missions use deterministic reserved schedules on a synchronous grid. Idle robots are held outside the shared graph and enter at their reserved start. Physical parking, holding-area transitions, communication delays, and stochastic execution delays are not modeled. Node-time and opposing-edge conflicts are checked before admission; complete pickup and delivery intervals are reserved.

Mission energy is checked against the battery floor and debited once using the realized route. Idle recharge uses elapsed idle time. Energy and retrieval-service coefficients are prescribed simulation inputs without industrial calibration. Waiting drain, charger queues, battery aging, and individual neighboring tote-relocation trajectories are not represented. Lower-capacity tests also lower initial stored energy in the finite episode.

Deep retrieval uses zero-based stack position and a support count. Unit-capacity blocking shares the source column and is redundant with source capacity under the stated inherited-occupancy assumptions. Nominal interface-capacity tests retain the same access nodes; physical-port tests provide distinct delivery nodes. Physical-tote uniqueness is imposed when jobs can share a tote and is redundant in the distinct-SKU benchmark.

External resupply attempts tote additions every 60 s without consuming AMR or interface capacity. Its prescribed quantity is `round(60 × baseline_rate × number_of_lines)` using ties-to-even rounding: 9 totes at base demand, 4 at half demand, and 14 at 1.5 demand. Each addition samples an unlocked column with spare capacity and a uniform SKU; additions stop when no space remains. Demand sensitivity therefore also changes this external supply quantity.

Gross completed missions include deliveries rejected at a full buffer and do not equal useful throughput. Overflow units leave the modeled flow without a return trip or separate overflow cost. The travel-relaxed counterfactual retains service and energy accounting while removing inter-robot travel conflicts; it is an analytical comparator.

## License and citation

The source project's `pyproject.toml` declares an MIT code license. A separate data license is not specified. Third-party dependencies retain their own terms, and Gurobi is not distributed in the payloads.

Please cite the repository and identify the release or commit used:

> Elyasi, M. (2026). AMR Replenishment: code and simulation data for shielded rolling-horizon optimization. Version 1.0.0. https://github.com/miladelyasi/AMR_Replenishment

Machine-readable citation metadata are provided in `CITATION.cff`.
