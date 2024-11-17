from src.utils.dataclass_utils import AppModel


class MappingMetrics(AppModel):
    total_comparisons: int = 0
    forced_matches: int = 0
    calculated_matches: int = 0
    avg_similarity: float = 0.0
    validation_failures: int = 0
    pulp_iterations: int = 0
    pulp_timeouts: int = 0
    pulp_cycles: int = 0
    pulp_cached_failures: int = 0

    def add_comparison(self, similarity: float, was_forced: bool):
        """Track a field comparison"""
        self.total_comparisons += 1
        if was_forced:
            self.forced_matches += 1
        else:
            self.calculated_matches += 1
            self.avg_similarity = (
                self.avg_similarity * (self.calculated_matches - 1) + similarity
            ) / self.calculated_matches

    def add_validation_failure(self):
        """Track a validation failure in PuLP"""
        self.validation_failures += 1

    def add_pulp_iteration(self):
        """Track a PuLP iteration"""
        self.pulp_iterations += 1

    def add_pulp_timeout(self):
        """Track a PuLP timeout"""
        self.pulp_timeouts += 1

    def add_pulp_cycle(self):
        """Track a PuLP cycle detection"""
        self.pulp_cycles += 1

    def add_pulp_cached_failure(self):
        """Track a cached PuLP failure (skipped retry)"""
        self.pulp_cached_failures += 1

    def get_summary(self) -> str:
        """Get a formatted summary of the metrics"""
        return (
            f"Mapping Metrics:\n"
            f"  Total comparisons: {self.total_comparisons}\n"
            f"  Forced matches: {self.forced_matches}\n"
            f"  Calculated matches: {self.calculated_matches}\n"
            f"  Avg similarity: {self.avg_similarity:.3f}\n"
            f"  Validation failures: {self.validation_failures}\n"
            f"  PuLP iterations: {self.pulp_iterations}\n"
            f"  PuLP timeouts: {self.pulp_timeouts}\n"
            f"  PuLP cycles: {self.pulp_cycles}\n"
            f"  PuLP cached failures: {self.pulp_cached_failures}\n"
        )

    def reset(self):
        """Reset all metrics to zero"""
        self.total_comparisons = 0
        self.forced_matches = 0
        self.calculated_matches = 0
        self.avg_similarity = 0.0
        self.validation_failures = 0
        self.pulp_iterations = 0
        self.pulp_timeouts = 0
        self.pulp_cycles = 0
        self.pulp_cached_failures = 0
