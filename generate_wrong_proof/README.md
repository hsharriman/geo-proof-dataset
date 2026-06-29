# Generate wrong proof

Current implemented wrong proof types:

```text
permutation_tree
permutation_non_tree
```

Not implemented yet:

```text
mixed_up_theorems
remove_step
circular_reasoning
```

Those files are currently only placeholders.



## How to run

Run the command from the folder that contains `generate_wrong_proof/`.

The folder should look like this:

```text
geo-proof-dataset/
├── generate_wrong_proof/
├── proofs/
└── wrong_proofs/
```

From:

```powershell
cd path\to\geo-proof-dataset
```

Run:

```powershell
python -m generate_wrong_proof.src.wrong_statement `
  --input-dir .\proofs `
  --output-dir .\wrong_proofs
```

**Do not run from inside `generate_wrong_proof/src/`**

Run on one file

```powershell
python -m generate_wrong_proof.src.wrong_statement `
  --input-dir .\proofs `
  --files holt_s4-4_exer13_c1.txt `
  --output-dir .\wrong_proofs
```

Generate all possible wrong proofs

```powershell
python -m generate_wrong_proof.src.wrong_statement `
  --input-dir .\proofs `
  --output-dir .\wrong_proofs `
  --all-possible
```

Generate wrong proofs with multiple mutations

```powershell
python -m generate_wrong_proof.src.wrong_statement `
  --input-dir .\proofs `
  --output-dir .\wrong_proofs `
  --all-possible `
  --mutations-per-proof <desired_number>
```

Replace `<desired_number>` with the number of mutations wanted for each wrong proof.

For example:

```powershell
python -m generate_wrong_proof.src.wrong_statement `
  --input-dir .\proofs `
  --output-dir .\wrong_proofs `
  --all-possible `
  --mutations-per-proof 2
```


## Choose mutation types

Only tree-based mutation:

```powershell
python -m generate_wrong_proof.src.wrong_statement `
  --input-dir .\proofs `
  --output-dir .\wrong_proofs `
  --mutation-types permutation_tree
```

Only non-tree mutation:

```powershell
python -m generate_wrong_proof.src.wrong_statement `
  --input-dir .\proofs `
  --output-dir .\wrong_proofs `
  --mutation-types permutation_non_tree
```


## Arguments

```text
--input-dir              folder with original proof files
--output-dir             folder to save wrong proofs
--metadata-out           path to save metadata JSONL
--files                  specific proof files
--glob                   file pattern, default *.txt
--limit                  only process first n files
--step                   mutate one specific step
--num-corruptions        number of wrong proofs to generate
--all-possible           generate every possible mutation chain
--mutations-per-proof    number of mutations in one wrong proof
--mutation-types         allowed mutation types
--require-mutation-types force some mutation types to appear
--seed                   random seed (default: 0)
```

## Output

Wrong proof files are saved to:

```text
wrong_proofs/
```

Metadata is saved to:

```text
wrong_proofs/wrong_statement_metadata.jsonl
```

Each metadata row records:

```text
source
output
wrong_id
num_mutations
mutation_types
mutation_groups
steps
edit_distance
mutation_score
mutations
```


## File notes

### `src/wrong_statement.py`

Main runner.

Does:
- read proof files
- choose candidate steps
- collect possible mutations
- generate mutation chains
- write wrong proof files
- write metadata


### `src/parsing/proof_parser.py`

Parses proof text.

Does:
- parse proof steps
- extract points
- extract segments
- parse statement predicate and arguments
- render statement back to text


### `src/geometry/geometry_objects.py`

Defines geometry object helpers.

Currently supports:
- point
- segment
- angle
- triangle
- quadrilateral
- circle


### `src/mutation/mutation_context.py`

Stores proof information used during mutation:

- steps
- points
- segments


### `src/mutation/mutation_types.py`

Defines mutation type registry and metadata helpers.

Registered mutation types:

- permutation_tree
- permutation_non_tree
- mixed_up_theorems
- remove_step
- circular_reasoning


### `src/mutation/mutation_collector.py`

Collects possible mutations.

Does:
- call each mutation method
- filter by allowed mutation types
- filter by required mutation types
- remove duplicate mutations


### `src/mutation/constraints.py`

Constraint checks for tree-based mutations.



### `src/mutation/methods/tree_permutation.py`

Controlled wrong statement mutation.

Can mutate:
- predicate
- geometry object

Examples:

```text
con_seg -> sim_seg
con_tri -> sim_tri
con_ang -> supplementary
AB -> AC
a_ABC -> a_ACB
t_ABC -> t_BAC
c_OA -> c_OB
```

Mutation type:

```text
permutation_tree
```

Corruption types:

```text
wrong_statement_tree_predicate
wrong_statement_tree_object
```

### `src/mutation/methods/non_control_permutation.py`

Less controlled argument mutation.

Changes one argument directly.

Mutation type:

```text
permutation_non_tree
```

Corruption type:

```text
wrong_statement_argument_permutation
```


### `src/mutation/methods/mixed_up_theorem.py`


### `src/mutation/methods/remove_step.py`


### `src/mutation/methods/circular_reasoning.py`


### `src/graphs/dependencies_tree.py`

Defines statement signatures and related predicate groups.

Contains:

```text
STATEMENT_SIGNATURES
PREDICATE_GROUPS
DIRECT_PREDICATE_EDGES
PREDICATE_TREE
STATEMENT_TREE
```

Used for predicate-level mutation.


### `src/graphs/predicate_graph.py`

Finds related predicates.


### `src/graphs/reason_families.py`

Manual theorem and reason groups.


### `src/graphs/reason_edge.py`

Utilities for building reason graph edges.


### `src/graphs/reason_edges/`

One file per reason family.

These manually define reason relationships.


### `src/graphs/reason_graph.py`

Builds the full reason graph from all reason-edge files


### `visualization/`

Reason graph visualization