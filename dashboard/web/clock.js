export function formatClock(ms) {
  const totalTenths = Math.floor(Math.max(0, ms) / 100);
  const tenths = totalTenths % 10;
  const totalSeconds = Math.floor(totalTenths / 10);
  const seconds = totalSeconds % 60;
  const minutes = Math.floor(totalSeconds / 60);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}.${tenths}`;
}

export function idleRun(name = "") {
  return { name, status: "idle", elapsedMs: 0, startedAt: null };
}

export function elapsed(run, now) {
  if (run.status === "running" && run.startedAt != null) {
    return run.elapsedMs + (now - run.startedAt);
  }
  return run.elapsedMs;
}

export function start(run, now) {
  if (run.status === "running") return run;
  return { ...run, status: "running", startedAt: now };
}

export function stop(run, now) {
  if (run.status !== "running") {
    return { ...run, status: "stopped", startedAt: null };
  }
  return { ...run, status: "stopped", elapsedMs: elapsed(run, now), startedAt: null };
}

export function reset(run) {
  return idleRun(run.name);
}
