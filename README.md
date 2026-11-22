# BAL — Bio-Availability Language

**Standalone release: v0.3.0**

BAL is an independent domain-specific research language and runtime for
normalized bioavailability modeling and DDS-inspired multi-compartment
simulation. It is maintained separately from BPL.

## Contents
The complete source distribution is provided in
`BAL_v0.3.0_standalone.tar.gz`. It contains the Python package, tests,
reference JSON scenario, documentation, MIT license, and GitHub Actions workflow.

## Quick start
Extract the archive, enter the extracted directory, then run:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
bal-sim --config examples/bal_multicompartment.json
```

## Model scope
The five-compartment model represents a DDS depot, gut, liver, plasma and tissue,
with cumulative loss compartments and a phenomenological tolerance state.
All example coefficients are synthetic software demonstration values, not
experimentally validated biological or clinical measurements. BAL is a research
prototype, not a clinical dosing or treatment recommendation system.

## Independence
BAL has its own repository, package, syntax roadmap, runtime and versioning.
It does not depend on BPL.
