# Donor session preregistration

Created before inspecting calibration outcomes. Choose the new variant with the
lowest sum of E/published_E across calibration lengths 99 and 119 and four seeds;
break ties using total solver CPU time. Freeze it before held-out runs. The four
candidates are iterated and population tabu, each with 4N or 12N stagnant-step
restart thresholds. Baseline tabu is an unchanged control.

Held-out test: lengths 92,99,107,119, eight seeds 3849692701..3849692708,
50 million single-bit neighbor evaluations per run, both unchanged tabu and the
selected variant, randomized execution order. Report all paired wins/ties/losses,
per-length median E, median paired change, CPU costs and distances to published E.
Do not select another variant after inspecting held-out results. Evaluation
counts are equal; archive/crossover/restart work is accounted in CPU time but
not neighbor counts. This is a comparison against the local baseline, not SOTA.

Then try the frozen variant from the four published witnesses using seeds
3849692701..3849692704 and 100 million evaluations. These are conditioned warm
starts and cannot be pooled with cold starts or advertised as rediscoveries.
Any extension requires an explicitly recorded exploratory scope. All results,
including timeouts, failures and unstarted planned jobs, remain in the log.
Stop search by 07:10:21 UTC, leaving 15 minutes for verification and handoff.
Hard session deadline: 07:25:21 UTC. Primary success is a strict published-energy
improvement, not an internal-baseline win.

## Interrupted-session amendment

At 13:04 UTC the user resumed the interrupted session. Calibration completed
in the background at 06:36:54.818652 UTC. Charge the entire first 693.818652
seconds and allow at most 2906 more seconds from 13:04:13 UTC. The experiment
is not an uninterrupted hour. Hard resumed deadline 13:52:39 UTC; search stops
13:37:39. Held-out search stops 13:28:39, reserving nine minutes for warm starts.
The variant was selected using the original criterion before any held-out run.
Shuffle paired jobs as blocks, randomizing within blocks, so time censoring
leaves few unmatched runs. The job list and all unstarted work are retained.
No scientific parameters or held-out seeds changed.
