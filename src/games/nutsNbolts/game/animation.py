from __future__ import annotations

from dataclasses import dataclass

Point = tuple[float, float]


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_in_cubic(t: float) -> float:
    return t * t * t


def ease_in_out_cubic(t: float) -> float:
    if t < 0.5:
        return 4 * t * t * t
    return 1 - pow(-2 * t + 2, 3) / 2


@dataclass
class MoveAnimation:
    source_index: int
    destination_index: int
    nut_color: str
    start: Point
    lift: Point
    drop_start: Point
    end: Point
    elapsed: float = 0.0
    lift_duration: float = 0.12
    travel_duration: float = 0.22
    drop_duration: float = 0.13

    @property
    def total_duration(self) -> float:
        return self.lift_duration + self.travel_duration + self.drop_duration

    def update(self, dt: float) -> bool:
        self.elapsed = min(self.total_duration, self.elapsed + dt)
        return self.elapsed >= self.total_duration

    def position(self) -> Point:
        if self.elapsed <= self.lift_duration:
            t = ease_out_cubic(self.elapsed / self.lift_duration)
            return (
                lerp(self.start[0], self.lift[0], t),
                lerp(self.start[1], self.lift[1], t),
            )

        travel_elapsed = self.elapsed - self.lift_duration
        if travel_elapsed <= self.travel_duration:
            t = ease_in_out_cubic(travel_elapsed / self.travel_duration)
            x = lerp(self.lift[0], self.drop_start[0], t)
            y = lerp(self.lift[1], self.drop_start[1], t) - 18 * (1 - abs(2 * t - 1))
            return (x, y)

        drop_elapsed = self.elapsed - self.lift_duration - self.travel_duration
        t = ease_in_cubic(drop_elapsed / self.drop_duration)
        return (
            lerp(self.drop_start[0], self.end[0], t),
            lerp(self.drop_start[1], self.end[1], t),
        )


@dataclass
class Shake:
    duration: float = 0.2
    elapsed: float = 0.0
    amplitude: float = 7.0

    def update(self, dt: float) -> bool:
        self.elapsed = min(self.duration, self.elapsed + dt)
        return self.elapsed >= self.duration

    def offset(self) -> float:
        if self.elapsed >= self.duration:
            return 0.0
        progress = self.elapsed / self.duration
        return self.amplitude * (1 - progress) * (-1 if int(progress * 20) % 2 else 1)


@dataclass
class Pulse:
    duration: float = 0.42
    elapsed: float = 0.0

    def update(self, dt: float) -> bool:
        self.elapsed = min(self.duration, self.elapsed + dt)
        return self.elapsed >= self.duration

    def amount(self) -> float:
        if self.duration <= 0:
            return 0.0
        p = self.elapsed / self.duration
        return max(0.0, 1 - p)
