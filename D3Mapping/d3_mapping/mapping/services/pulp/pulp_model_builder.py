from dataclasses import dataclass

import pulp


@dataclass
class PulpMappingData:
    """Data structure for PuLP mapping."""

    sim_by_mapping: dict[tuple[tuple[str, ...], tuple[str, ...]], float]
    reliability_by_mapping: dict[tuple[tuple[str, ...], tuple[str, ...]], float]


@dataclass
class PulpModel:
    """PuLP model with variables."""

    model: pulp.LpProblem
    variables: dict[tuple[tuple[str, ...], tuple[str, ...]], pulp.LpVariable]


class PulpModelBuilder:
    """Builds PuLP optimization models for field mapping."""

    def build(self, mapping_data: PulpMappingData) -> PulpModel:
        """Build a complete PuLP model with all constraints.

        Args:
            ctx: Comparison context
            mapping_data: Similarity and reliability data for all field pairs

        Returns:
            PulpModel with LP problem and variables
        """
        model = pulp.LpProblem("BestPathMapping", pulp.LpMaximize)
        variables = self._create_variables(mapping_data.sim_by_mapping)

        self._add_parent_constraints(model, variables)
        self._add_uniqueness_constraints(model, variables)
        self._add_objective(model, mapping_data.sim_by_mapping, variables)

        return PulpModel(model=model, variables=variables)

    def _create_variables(
        self, sim_by_mapping: dict[tuple[tuple[str, ...], tuple[str, ...]], float]
    ) -> dict[tuple[tuple[str, ...], tuple[str, ...]], pulp.LpVariable]:
        """Create binary variables for each mapping pair."""
        variables = {}
        for clear_path, obf_path in sim_by_mapping:
            var_name = f"map_{'_'.join(clear_path)}__{'_'.join(obf_path)}"
            variables[(clear_path, obf_path)] = pulp.LpVariable(var_name, cat="Binary")
        return variables

    def _add_parent_constraints(
        self,
        model: pulp.LpProblem,
        variables: dict[tuple[tuple[str, ...], tuple[str, ...]], pulp.LpVariable],
    ):
        """Add constraints: child can only be selected if parent is selected."""
        for (clear_path, obf_path), var in variables.items():
            for i in range(1, len(clear_path)):
                clear_parent = clear_path[:i]
                obf_parent = obf_path[:i]
                parent_var = variables[(clear_parent, obf_parent)]
                model += (
                    var <= parent_var,
                    f"parent_constraint_{var.name}_le_{parent_var.name}",
                )

    def _add_uniqueness_constraints(
        self,
        model: pulp.LpProblem,
        variables: dict[tuple[tuple[str, ...], tuple[str, ...]], pulp.LpVariable],
    ):
        """Add constraints: each path can only be mapped once."""
        pairs_by_path: dict[tuple[str, ...], list] = {}
        for clear_path, obf_path in variables.keys():
            pairs_by_path.setdefault(clear_path, []).append((clear_path, obf_path))
            pairs_by_path.setdefault(obf_path, []).append((clear_path, obf_path))

        for pairs in pairs_by_path.values():
            model += pulp.lpSum(variables[pair] for pair in pairs) <= 1

    def _add_objective(
        self,
        model: pulp.LpProblem,
        sim_by_mapping: dict[tuple[tuple[str, ...], tuple[str, ...]], float],
        variables: dict[tuple[tuple[str, ...], tuple[str, ...]], pulp.LpVariable],
    ):
        """Add objective function: maximize total similarity."""
        model += pulp.lpSum(
            sim_by_mapping[(clear_path, obf_path)] * variables[(clear_path, obf_path)]
            for (clear_path, obf_path) in sim_by_mapping
        )

    def add_exclusion_constraint(
        self, model: pulp.LpProblem, pulp_model: PulpModel, failed_mapping: set
    ):
        """Add constraint to exclude a failed mapping combination."""
        model += (
            pulp.lpSum(pulp_model.variables[pair] for pair in failed_mapping)
            <= len(failed_mapping) - 1
        )
