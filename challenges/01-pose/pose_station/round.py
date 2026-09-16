from dataclasses import dataclass

from pose_station.matcher import is_in_pose, score_pose


@dataclass(frozen=True)
class RoundState:
    pose_index: int
    pose_total: int
    hold_ratio: float
    score: float
    in_pose: bool
    person_present: bool
    station_complete: bool
    prompt: str
    tint: str
    just_advanced: bool


def _tint(score: float, matched: bool) -> str:
    if matched:
        return "green"
    if score >= 0.5:
        return "yellow"
    return "red"


class RoundEngine:
    def __init__(self, poses: list[dict]):
        if not poses:
            raise ValueError("need at least one pose")
        self._poses = poses
        self.restart()

    def restart(self) -> None:
        self._index = 0
        self._hold = 0.0
        self._complete = False

    @property
    def current_pose(self) -> dict:
        return self._poses[self._index]

    def update(self, dt: float, landmarks: dict | None) -> RoundState:
        total = len(self._poses)
        person = bool(landmarks)

        if self._complete:
            return RoundState(
                pose_index=self._index,
                pose_total=total,
                hold_ratio=1.0,
                score=1.0,
                in_pose=True,
                person_present=person,
                station_complete=True,
                prompt="POSE STATION CLEAR",
                tint="green",
                just_advanced=False,
            )

        if not person:
            self._hold = 0.0
            return RoundState(
                pose_index=self._index,
                pose_total=total,
                hold_ratio=0.0,
                score=0.0,
                in_pose=False,
                person_present=False,
                station_complete=False,
                prompt="Stand in frame",
                tint="red",
                just_advanced=False,
            )

        pose = self.current_pose
        score = score_pose(landmarks, pose["angles"])
        matched = is_in_pose(score)
        just_advanced = False

        if not matched:
            self._hold = 0.0
            ratio = 0.0
        else:
            self._hold += dt
            needed = float(pose["hold_seconds"])
            if self._hold >= needed:
                just_advanced = True
                self._hold = 0.0
                if self._index >= total - 1:
                    self._complete = True
                else:
                    self._index += 1
            ratio = 1.0 if self._complete else 0.0 if just_advanced else min(
                1.0, self._hold / needed
            )

        if self._complete:
            prompt = "POSE STATION CLEAR"
            tint = "green"
        else:
            prompt = f"POSE {self._index + 1} / {total}"
            tint = _tint(score, matched)

        return RoundState(
            pose_index=self._index,
            pose_total=total,
            hold_ratio=ratio,
            score=score,
            in_pose=matched,
            person_present=True,
            station_complete=self._complete,
            prompt=prompt,
            tint=tint,
            just_advanced=just_advanced,
        )
