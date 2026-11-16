# Technical round 2: measured numbers for the module-level change picture

Run on 2026-11-16. Every number below was produced by a script on this machine. Nothing is estimated. Times are seconds, printed exactly as the scripts printed them.

Work directory (session scratchpad, may be cleared later): `/tmp/claude-0/-home-user-explain-pr/074e39f7-08cf-5ec8-b66b-62906beb6d01/scratchpad/tech2/` (called `$B` below).

## What the numbers say

- **Full Python import graph with `ast`**: 0.12 to 0.20 s for flask (83 modules), 4.5 to 5.5 s for django (2,943 modules), 9.8 to 10.7 s for sympy (1,609 modules, 814,376 lines). For django and sympy over 99% of that time is reading and parsing files; resolving edges takes under 0.03 s.
- **Updating the graph for one commit**: 0.012 to 0.10 s without writing the cache back, 0.014 to 0.19 s with it. The result matched a full rebuild in all three repositories.
- **tree-sitter** gave the same edges as `ast` in 5.7 to 6.6 s for sympy and 3.1 to 3.6 s for django, against 9.8 to 10.7 s and 4.5 to 5.5 s for `ast`. For re-parsing two changed files, it saved less time than its own 0.016 to 0.037 s of import and setup cost.
- **Typical change picture**: the median commit touches 2 files in all three repositories. "Changed second-level modules plus direct dependents, grouped at second level" is 20 boxes or fewer for 96.5% (flask), 93.5% (django) and 83% (sympy) of the last 200 non-merge commits. The worst cases are 51, 210 and 65 boxes.
- **Dependents are the part that grows**: the count of direct dependent modules has a 90th percentile of 8 (flask), 22 (django) and 190 (sympy), and a maximum of 822. Grouping at second level brings the sympy 90th percentile down to 27.
- **`git diff`**: `--name-status` with or without `-M` takes 0.002 to 0.006 s warm and 0.011 to 0.036 s with the disk cache dropped. `--stat` over 50 commits is the only slow one, at 0.075 to 0.15 s.
- **TypeScript**: on vuejs/core, dependency-cruiser took 2.5 to 2.6 s and madge took 5.3 to 5.8 s. madge did not follow the `tsconfig.json` path aliases, so it found 1 edge into `shared/src/index.ts` from other packages where dependency-cruiser found 160.

## Machine facts

| Fact | Raw value |
|---|---|
| `nproc` | 4 |
| `free -m` | Mem: total 16087, used 636, free 14991, buff/cache 694, available 15451; Swap 0 |
| `python3 --version` | Python 3.13.18 |
| CPU (`lscpu`) | Intel(R) Xeon(R) Processor @ 2.10GHz, 4 cores, 1 thread per core, KVM guest |
| `git --version` | 2.43.0 |
| `node --version`, `npm --version` | v22.23.4, 10.9.9 |
| Disk | `/dev/vda`, 252G, 24G free |

All Python scripts are single-threaded. No parallel run was measured.

## Scripts

All under `$B/scripts/`:

| Path | Purpose |
|---|---|
| `$B/scripts/pygraph.py` | Shared graph code: list files, name modules, extract imports with `ast`, resolve edges |
| `$B/scripts/m12_build.py` | Measurements 1 and 2: one full build per process, timed by phase |
| `$B/scripts/m2_incremental.py` | Measurement 2: incremental update, with a check against a full build |
| `$B/scripts/m3_commits.py` | Measurement 3: per-commit sizes and distributions |
| `$B/scripts/m4_gitdiff.py` | Measurement 4: `git diff` timings |
| `$B/scripts/m5_treesitter.py` | Measurement 5: the same graph with tree-sitter |

Raw outputs are in `$B/out/` (`m12_raw.txt`, `m2_incr_raw.txt`, `m3_<repo>.json`, `m3_<repo>.csv` with one row per commit, `m4_raw.txt`, `m5_raw.txt`, `madge*.json`, `dc*.json`).

All Python was run with `python3 -I`. Repository files were only read as bytes and parsed. No repository code was imported, run or installed.

## Measurement 1: the repositories

Clone command, run in `$B/repos/`: `git clone -q --depth 400 https://github.com/<owner>/<name>.git <name>`

| | flask | django | sympy |
|---|---|---|---|
| HEAD | `49943b5a94413a530761350f04e896f76e8d620e` | `d3954c981368eb4439be63f2f165d400f33bcd70` | `8261008e1c6188c346ba557ed37b45f78bf761a5` |
| HEAD commit date | 2026-10-30T08:05:20-07:00 | 2026-11-16T11:15:23-05:00 | 2026-11-16T20:09:43+01:00 |
| Clone wall time (s) | 1.574160109 | 4.177449613 | 24.772197384 |
| Commits fetched (`rev-list --count HEAD`) | 1466 | 400 | 60199 |
| Non-merge commits fetched | 851 | 400 | 47884 |
| Size on disk (`du -sh`) | 7.4M | 88M | 228M |
| Tracked files, all types (`git ls-files`) | 236 | 7104 | 2096 |
| Tracked `*.py` files, which is the module count | 83 | 2943 | 1609 |
| Lines of Python (newline bytes in those files) | 18392 | 532033 | 814376 |
| Distinct dotted module names | 81 | 2941 | 1608 |
| Files that failed `ast.parse` | 0 | 1 | 0 |

`--depth 400` fetched far more than 400 commits for flask and sympy because depth counts along every parent path and both histories are full of merges.

The one django parse failure is `tests/test_runner_apps/tagged/tests_syntax_error.py` (`SyntaxError: invalid decimal literal`, line 11), a deliberate test fixture. It stays in the graph as a node with no outgoing edges.

"Largest" depends on the measure: sympy has the most Python lines and the most history, django has the most files and modules.

## Measurement 2: import graph with standard-library `ast`

### Rules of the graph (each is an approximation)

1. A module is one tracked `*.py` file. Untracked and generated files are not included.
2. The dotted name is built by walking up from the file while the directory has a tracked `__init__.py`. Namespace packages (directories without `__init__.py`) are therefore not recognised: django's `tests/` has none, so `tests/admin_views/tests.py` is named `admin_views.tests` and each test app counts as its own top-level package.
3. When two files get the same dotted name, the first in sorted path order keeps the name. The other stays as a node and can import, but nothing can resolve to it. Collisions: flask 2, django 2, sympy 1.
4. Every `import` and `from ... import` anywhere in a file counts, including ones inside functions, inside `try`/`except` and under `if TYPE_CHECKING:`.
5. `import a.b.c` gives one edge to the longest prefix that is a repository module. `from a.b import c` gives an edge to `a.b.c` if that is a module, otherwise to `a.b`.
6. Relative imports are resolved against the importing file's package.
7. Dynamic imports (`importlib.import_module`, `__import__`, string settings such as django's `INSTALLED_APPS`) are not seen.
8. An edge is a distinct (source file, target file) pair. Self-edges are dropped.

### Graph size

| | flask | django | sympy |
|---|---|---|---|
| Nodes (modules) | 83 | 2943 | 1609 |
| Import records found | 675 | 19488 | 39364 |
| Edges resolved inside the repository | 176 | 9109 | 14305 |
| Modules with at least one outgoing edge | 75 | 2140 | 1456 |

### Full build times

Command, one fresh process per run: `python3 -I $B/scripts/m12_build.py $B/repos/<repo>`

"Cold" means `sync; echo 3 > /proc/sys/vm/drop_caches` was run before the run, so files came from disk. "Warm" means the files were already in the OS cache. `t_total_s` is measured inside the script and excludes interpreter start. `process_wall_s` is measured from the shell and includes it.

| Repo | Run | `t_total_s` | `process_wall_s` | of which `t_read_and_ast_parse_s` |
|---|---|---|---|---|
| flask | cold 1 | 0.14295264200001156 | .196273395 | 0.13319171899996718 |
| flask | cold 2 | 0.18245092900002646 | .240486780 | 0.17361422399994808 |
| flask | cold 3 | 0.1988289089999853 | .249161865 | 0.1904689860000417 |
| flask | warm 1 | 0.1340062530000523 | .175198922 | 0.1312354629999959 |
| flask | warm 2 | 0.12309083100001317 | .156370642 | 0.11937606599997252 |
| flask | warm 3 | 0.12745333800000935 | .164996959 | 0.12457622499999843 |
| django | cold 1 | 5.511652739999988 | 5.586757487 | 5.476578335999989 |
| django | cold 2 | 5.403329162999967 | 5.471177500 | 5.367098614000042 |
| django | cold 3 | 5.1264864969999735 | 5.178349447 | 5.09643964899999 |
| django | warm 1 | 4.506434768999952 | 4.548166139 | 4.482410431999995 |
| django | warm 2 | 4.759407979999992 | 4.809287917 | 4.728172639000036 |
| django | warm 3 | 4.9492398019999655 | 5.006804225 | 4.924400725999988 |
| sympy | cold 1 | 10.574524941999982 | 10.637019880 | 10.542292695000015 |
| sympy | cold 2 | 10.749956141999974 | 10.811148193 | 10.716504087999965 |
| sympy | cold 3 | 10.677703841999971 | 10.765562507 | 10.642252702999997 |
| sympy | warm 1 | 10.574201490000007 | 10.613806213 | 10.547773503999963 |
| sympy | warm 2 | 9.80801782399999 | 9.852148206 | 9.78387167599999 |
| sympy | warm 3 | 10.598678511000003 | 10.650059042 | 10.564573476000021 |

Other phases, ranges over the same 18 runs:

| Phase | flask | django | sympy |
|---|---|---|---|
| `git ls-files` (`t_git_ls_files_s`) | 0.0022 to 0.0092 | 0.0049 to 0.0118 | 0.0029 to 0.0113 |
| Naming modules (`t_name_modules_s`) | 0.00015 to 0.00022 | 0.0059 to 0.0096 | 0.0033 to 0.0056 |
| Resolving edges (`t_resolve_edges_s`) | 0.00033 to 0.00061 | 0.0132 to 0.0193 | 0.0178 to 0.0271 |

Those ranges are the smallest and largest raw values in `$B/out/m12_raw.txt`, shortened to two significant digits for the table; the file has the full values.

Writing the per-file import records as a JSON cache (one extra run with `--save`): flask 0.0017527800000038951 s for 23089 bytes, django 0.04961395300000504 s for 877704 bytes, sympy 0.06172581200002014 s for 1683086 bytes.

### Incremental update for the latest commit

Commands:

```
python3 -I $B/scripts/m2_incremental.py $B/repos/<repo> $B/out/<repo>.cache.json --prep   $B/out/<repo>.old.json HEAD   # untimed setup
python3 -I $B/scripts/m2_incremental.py $B/repos/<repo> $B/out/<repo>.cache.json --update $B/out/<repo>.old.json HEAD   # timed
```

The setup step makes a cache as of `HEAD~1` by parsing the old version of each changed file from `git show HEAD~1:<path>`. The timed step loads that cache, asks git which `*.py` files `HEAD~1..HEAD` changed, re-parses only those from the working tree, renames modules and re-resolves every edge, then writes the cache back. Each timed run reported `matches_full_build: true` (compared edge by edge with a fresh full build, outside the timed section).

Files re-parsed: flask 1 (`src/flask/app.py`), django 2 (`django/contrib/gis/gdal/geojson.py`, `tests/gis_tests/test_geoforms.py`), sympy 2 (`sympy/algebras/quaternion.py`, `sympy/algebras/tests/test_quaternion.py`).

| Repo | Run | `t_total_s` (with cache write) | `t_total_without_save_s` | `t_reparse_changed_s` |
|---|---|---|---|---|
| flask | cold 1 | 0.04075937099997873 | 0.03840585199998259 | 0.024391258999969523 |
| flask | cold 2 | 0.02364707899999985 | 0.021652646000006825 | 0.009820353000009163 |
| flask | cold 3 | 0.028249452000011388 | 0.02585208400000738 | 0.01325994600000513 |
| flask | warm 1 | 0.019153560000006564 | 0.016978272000017114 | 0.01187707799999771 |
| flask | warm 2 | 0.016821753999977318 | 0.014728170000012142 | 0.01078359600001022 |
| flask | warm 3 | 0.013765714000044227 | 0.01211335000004965 | 0.008571361999997862 |
| django | cold 1 | 0.08959358099997417 | 0.054650838999975804 | 0.011753340999973716 |
| django | cold 2 | 0.09122620099998358 | 0.060043442999983654 | 0.009878469999989647 |
| django | cold 3 | 0.08220304100001385 | 0.047560657000019546 | 0.009447700999999142 |
| django | warm 1 | 0.07536865499997702 | 0.04021388400002479 | 0.007997461999991629 |
| django | warm 2 | 0.10259094200000618 | 0.0527697380000518 | 0.01108144500005892 |
| django | warm 3 | 0.07231659900003251 | 0.037866289000021425 | 0.008044201999950928 |
| sympy | cold 1 | 0.12726560999999492 | 0.07221996900000249 | 0.021606499000085932 |
| sympy | cold 2 | 0.18070267999996759 | 0.0922551989999647 | 0.02859703499996158 |
| sympy | cold 3 | 0.1857184169999755 | 0.10061948700001722 | 0.03044599300005757 |
| sympy | warm 1 | 0.15581685999995898 | 0.07375655199996345 | 0.02428509200001372 |
| sympy | warm 2 | 0.11551947600003132 | 0.06180051900003036 | 0.018973094999978457 |
| sympy | warm 3 | 0.15480400499995994 | 0.07540436700003283 | 0.023439204000055724 |

For django and sympy the largest single phase of an update is writing the JSON cache back (0.031 to 0.088 s), then loading it (0.010 to 0.026 s). All phase times per run are in `$B/out/m2_incr_raw.txt`.

Approximations in this measurement:

- These times exclude Python interpreter start. The full-build runs show that start costs about 0.03 to 0.09 s (`process_wall_s` minus `t_total_s`).
- flask's and sympy's HEAD are merge commits, so `HEAD~1..HEAD` is the diff against the first parent, which is what the merge brought in.
- All three latest commits only modified files. An update that adds or deletes a module was not measured. The script handles it by the same path (it always re-resolves all edges), but no timing exists for that case.
- Only small commits (1 or 2 Python files) were timed.

## Measurement 3: how big a typical change picture is

Command: `python3 -I $B/scripts/m3_commits.py $B/repos/<repo> $B/out/m3_<repo>.csv 200 > $B/out/m3_<repo>.json`

Commits come from `git log --no-merges -n 200 -M --name-status`. Script wall time including one full graph build: flask .204833376 s, django 7.060332254 s, sympy 11.174610902 s.

Sample range: flask `f622b1ca` to `bfc8f983`, django `abb9c04b` to `d3954c98`, sympy `a1ecd05c` to `e96b437c`. None of the 600 commits is a shallow-clone boundary commit (checked against `.git/shallow`), so every diff is against a real parent.

Approximations:

- **Dependents use the graph at HEAD, not the graph as of each commit.** A module that imported the changed module at commit time but no longer does is missed, and one that started importing it later is counted.
- Changed `*.py` files that no longer exist at HEAD are not in the graph and contribute nothing to module counts or dependents. This affects 1 file in 1 flask commit, 0 in django, and 6 files in 3 sympy commits.
- A rename counts as one file under its new path.
- "Top-level package" and "second-level module" are reported two ways. **By path**: first path component and first two path components, over all changed files. **By module name**: first dotted component and first two dotted components, over changed Python files only. For flask the second dotted level is a single file (`flask.app`); for sympy it is a subpackage (`sympy.core`).
- Test modules are part of the graph and count as dependents.
- Percentiles are nearest-rank (the value at sorted position `ceil(p*n)`), so every figure is an observed value.
- `boxes_py` = distinct second-level names among changed modules and their direct dependents. `boxes_all` adds one box per second-level path group of changed non-Python files.

### All 200 commits

Each cell is median / 75th percentile / 90th percentile / maximum.

| Quantity | flask | django | sympy |
|---|---|---|---|
| (a) Files changed | 2 / 4 / 7 / 36 | 2 / 4 / 8 / 140 | 2 / 3 / 5 / 191 |
| Python files changed | 0 / 1 / 2 / 16 | 1 / 2 / 4 / 96 | 1 / 2 / 4 / 159 |
| (b) Top-level, by path | 1 / 2 / 3 / 7 | 2 / 3 / 3 / 6 | 1 / 1 / 2 / 4 |
| (b) Second-level, by path | 2 / 3 / 5 / 30 | 2 / 3 / 4 / 21 | 1 / 2 / 2 / 26 |
| (b) Top-level packages, by module name | 0 / 1 / 2 / 8 | 1 / 2 / 2 / 12 | 1 / 1 / 1 / 2 |
| (b) Second-level modules, by module name | 0 / 1 / 2 / 16 | 1 / 2 / 3 / 21 | 1 / 1 / 2 / 25 |
| (c) Direct dependent modules | 0 / 6 / 8 / 52 | 1 / 8 / 22 / 365 | 6 / 37 / 190 / 822 |
| Dependents grouped at second level | 0 / 6 / 8 / 50 | 1 / 5 / 12 / 200 | 3 / 12 / 27 / 64 |
| `boxes_py` | 0 / 7 / 11 / 51 | 2 / 6 / 13 / 210 | 3 / 12 / 27 / 65 |
| `boxes_all` | 3 / 8 / 12 / 52 | 3 / 7 / 14 / 213 | 3 / 13 / 27 / 65 |
| Share with `boxes_py` of 20 or fewer | 193/200 = 0.965 | 187/200 = 0.935 | 166/200 = 0.83 |
| Share with `boxes_all` of 20 or fewer | 190/200 = 0.95 | 186/200 = 0.93 | 166/200 = 0.83 |
| Commits that change no Python file | 111 | 67 | 34 |

One sympy commit in the sample changes 0 files (an empty commit), which is why sympy minimums are 0.

### Only commits that change at least one Python file present at HEAD

These are the commits for which an import picture has anything to show: 89 for flask, 133 for django, 165 for sympy.

| Quantity | flask (89) | django (133) | sympy (165) |
|---|---|---|---|
| Files changed | 3 / 6 / 11 / 36 | 3 / 5 / 12 / 140 | 2 / 3 / 5 / 191 |
| Python files changed | 1 / 2 / 5 / 16 | 2 / 3 / 6 / 96 | 2 / 3 / 5 / 159 |
| Second-level modules, by module name | 1 / 2 / 5 / 16 | 2 / 2 / 4 / 21 | 1 / 1 / 2 / 25 |
| Direct dependent modules | 6 / 8 / 11 / 52 | 5 / 14 / 29 / 365 | 12 / 46 / 294 / 822 |
| Dependents grouped at second level | 6 / 8 / 11 / 50 | 2 / 6 / 18 / 200 | 4 / 13 / 29 / 64 |
| `boxes_py` | 7 / 10 / 16 / 51 | 4 / 8 / 20 / 210 | 4 / 13 / 29 / 65 |
| `boxes_all` | 9 / 12 / 25 / 52 | 5 / 9 / 22 / 213 | 4 / 13 / 29 / 65 |
| Share with `boxes_py` of 20 or fewer | 82/89 = 0.9213483146067416 | 120/133 = 0.9022556390977443 | 131/165 = 0.793939393939394 |
| Share with `boxes_all` of 20 or fewer | 79/89 = 0.8876404494382022 | 119/133 = 0.8947368421052632 | 131/165 = 0.793939393939394 |

## Measurement 4: `git diff` timings

Command: `python3 -I $B/scripts/m4_gitdiff.py $B/repos/<repo> [--drop]`. Each `git diff` is a child process with output captured; three runs each. With `--drop` the OS cache is dropped before every single run. Run on sympy (most lines and history) and on django (most files).

Diff sizes: sympy `HEAD~1..HEAD` is 2 files (+85 −6), `HEAD~50..HEAD` is 140 files (+2892 −886). django `HEAD~1..HEAD` is 7 files (+51 −1), `HEAD~50..HEAD` is 275 files (+3438 −1835). On sympy `HEAD~50` follows first parents through merges.

### sympy

| Command | Cache | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|
| `git diff --stat HEAD~1 HEAD` | cold | 0.03107466899996325 | 0.019265238000002682 | 0.019856749999917156 |
| `git diff --name-status HEAD~1 HEAD` | cold | 0.017638519000001907 | 0.01455028600003061 | 0.018134173000021292 |
| `git diff -M --name-status HEAD~1 HEAD` | cold | 0.020175922000021274 | 0.01569813100002193 | 0.016422749999946973 |
| `git diff --stat HEAD~50 HEAD` | cold | 0.12282211800004461 | 0.14163424499997745 | 0.1440768360000675 |
| `git diff --name-status HEAD~50 HEAD` | cold | 0.029845808999994006 | 0.031299673000035 | 0.024632377999978416 |
| `git diff -M --name-status HEAD~50 HEAD` | cold | 0.027660954999987553 | 0.03251375699994696 | 0.036452648000022236 |
| `git diff --stat HEAD~1 HEAD` | warm | 0.0056910940000989285 | 0.0036195339999949283 | 0.0036187350000318474 |
| `git diff --name-status HEAD~1 HEAD` | warm | 0.0021061299999018956 | 0.0020877100000689097 | 0.0019929490000549777 |
| `git diff -M --name-status HEAD~1 HEAD` | warm | 0.002243604000000232 | 0.0026888160000453354 | 0.0024178930000289256 |
| `git diff --stat HEAD~50 HEAD` | warm | 0.10119046800002707 | 0.08237843599999906 | 0.07927535700002863 |
| `git diff --name-status HEAD~50 HEAD` | warm | 0.004960192999988067 | 0.004533609999953114 | 0.004528924000055667 |
| `git diff -M --name-status HEAD~50 HEAD` | warm | 0.004251161000070169 | 0.003756183000064084 | 0.004497143000094184 |

### django

| Command | Cache | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|
| `git diff --stat HEAD~1 HEAD` | cold | 0.021335625000006075 | 0.01651188899995759 | 0.016246071999944434 |
| `git diff --name-status HEAD~1 HEAD` | cold | 0.010664620999932595 | 0.01901788600002874 | 0.016283296999972663 |
| `git diff -M --name-status HEAD~1 HEAD` | cold | 0.017674009999950613 | 0.015657955999927253 | 0.016771976000086397 |
| `git diff --stat HEAD~50 HEAD` | cold | 0.11466718099995887 | 0.10318814100003237 | 0.1502054259999568 |
| `git diff --name-status HEAD~50 HEAD` | cold | 0.030704947000003813 | 0.028449877999946693 | 0.03267218000007688 |
| `git diff -M --name-status HEAD~50 HEAD` | cold | 0.028111867000006896 | 0.024273397999991175 | 0.025276761000100123 |
| `git diff --stat HEAD~1 HEAD` | warm | 0.005147706000002472 | 0.005477192000057585 | 0.00494864500001313 |
| `git diff --name-status HEAD~1 HEAD` | warm | 0.0028856980000000476 | 0.0029616860000487577 | 0.002885401000071397 |
| `git diff -M --name-status HEAD~1 HEAD` | warm | 0.0040291199999273886 | 0.0026399800000262985 | 0.0024003809999157966 |
| `git diff --stat HEAD~50 HEAD` | warm | 0.0984810859999925 | 0.07482028700007959 | 0.09478073200000381 |
| `git diff --name-status HEAD~50 HEAD` | warm | 0.006200020000051154 | 0.00549702899991189 | 0.005188188000033733 |
| `git diff -M --name-status HEAD~50 HEAD` | warm | 0.004783829000075457 | 0.004996731999995063 | 0.004554980000079922 |

Rename detection (`-M`) made no measurable difference at these sizes. Neither 50-commit range was checked for how many renames it actually contains, so this says nothing about a rename-heavy diff.

## Measurement 5: tree-sitter

Install succeeded: `python3 -m venv $B/venv; $B/venv/bin/pip install tree-sitter tree-sitter-python` gave tree-sitter 0.26.1 and tree-sitter-python 0.25.0.

Command: `$B/venv/bin/python -I $B/scripts/m5_treesitter.py $B/repos/<repo> [--compare | --only-changed HEAD]`

The script parses each file with tree-sitter, pulls import statements with one query (`(import_statement) @imp (import_from_statement) @frm`), and uses the same naming and edge-resolution code as the `ast` build. `t_total_s` includes importing and setting up tree-sitter.

Agreement with `ast` (`--compare`):

- sympy: 14305 edges from both, 0 differences. Import records differ (37894 against 39364) because the query does not capture `from __future__ import`, which tree-sitter gives its own node type; sympy has 1468 such lines. These never resolve to a repository module, so edges are unaffected. The remaining difference of 2 records was not traced.
- django: 9110 edges against 9109. The one extra edge is from the deliberately broken file `tests/test_runner_apps/tagged/tests_syntax_error.py`, which `ast` rejects whole and tree-sitter parses around the error.

### Full build

| Repo | Run | `t_total_s` | `t_read_parse_extract_s` | `t_import_and_setup_tree_sitter_s` |
|---|---|---|---|---|
| sympy | cold 1 | 6.614043933000062 | 6.557341269999938 | 0.02389528900005189 |
| sympy | cold 2 | 6.095446423999988 | 6.035883907000084 | 0.025030562999972972 |
| sympy | cold 3 | 5.882420918999969 | 5.813233246999971 | 0.027648543999930553 |
| sympy | warm 1 | 5.721513949000041 | 5.677554753999971 | 0.01815932600004544 |
| sympy | warm 2 | 5.65888741699996 | 5.619749643999967 | 0.016846537999981592 |
| sympy | warm 3 | 6.053469303000043 | 6.014309532000084 | 0.016700759000059406 |
| django | cold 1 | 3.347753420999993 | 3.285013041999946 | 0.029374329000006583 |
| django | cold 2 | 3.6363077059999114 | 3.5827444770000056 | 0.02434225100000731 |
| django | cold 3 | 3.2546896680000827 | 3.194942047999916 | 0.02897389600002498 |
| django | warm 1 | 3.404461019999985 | 3.3628304410000283 | 0.015976712999986376 |
| django | warm 2 | 3.0768324150000126 | 3.030190912999956 | 0.022113533000037933 |
| django | warm 3 | 3.2416873449999457 | 3.203491926999959 | 0.016035392999924625 |

### Re-parsing only the files changed by HEAD

Same two files per repository as in measurement 2. This times reading, parsing and extracting only; the cache load, re-resolve and cache write around it do not depend on the parser and are in measurement 2.

| Repo | Run | `t_read_parse_extract_changed_s` | `t_import_and_setup_tree_sitter_s` |
|---|---|---|---|
| sympy | cold 1 | 0.01619734899998093 | 0.031112591999999495 |
| sympy | cold 2 | 0.017748663000020315 | 0.03694314899996698 |
| sympy | cold 3 | 0.01840024299997367 | 0.03157396599999629 |
| sympy | warm 1 | 0.0177145999999766 | 0.023622546000069633 |
| sympy | warm 2 | 0.016031357999963802 | 0.02133234400002948 |
| sympy | warm 3 | 0.017749169000012444 | 0.023276854999949137 |
| django | cold 1 | 0.010515048000002025 | 0.028845202999946196 |
| django | cold 2 | 0.007563028000049599 | 0.02467901600005007 |
| django | cold 3 | 0.01075338800001191 | 0.03488419600000725 |
| django | warm 1 | 0.005650593000041226 | 0.016691841000010754 |
| django | warm 2 | 0.0053791410000485484 | 0.017325647999996363 |
| django | warm 3 | 0.00526694799998495 | 0.02266395499998453 |

The matching `ast` figure is `t_reparse_changed_s` in measurement 2: 0.019 to 0.030 s for sympy and 0.008 to 0.012 s for django. tree-sitter's own edit-and-reparse feature (reusing an old tree) was not used or measured; each file was parsed from scratch.

## Measurement 6: TypeScript module graph

Repository: `git clone -q --depth 1 https://github.com/vuejs/core.git vue-core`, HEAD `cbd95955a5362b44060908f6e28ad447c3031b8a`. 704 tracked files, 491 `*.ts`/`*.tsx` files with 168412 lines, of which 455 are under `packages/`.

Both tools were run with `npx` from an empty directory (`$B/npmrun`) with the npm cache in `$B/npmcache`, pointed at `packages/`. Nothing was installed in the repository and none of its scripts ran. Both tools worked.

### madge 8.0.0

Command: `npx --yes madge --json --extensions ts,tsx --ts-config $B/repos/vue-core/tsconfig.json $B/repos/vue-core/packages`

| Run | Wall time (s) |
|---|---|
| 1, includes downloading madge from npm | 13.962296187 |
| 2 | 5.824072842 |
| 3 | 5.345299832 |
| 4 | 5.319668121 |
| Without `--ts-config` (one run) | 4.898347548 |

Result: 455 nodes, 1334 edges, 53 edges between different packages, 84 nodes with no outgoing edge. Output was byte-identical between run 1 and run 4.

The output with `--ts-config` and without it has the same node and edge counts. The source has 478 lines that import `'@vue/<pkg>'` or `'vue'` through the `paths` aliases in `tsconfig.json`, and madge's graph has 1 edge into `shared/src/index.ts` from outside the `shared` package. So madge, as invoked here, did not resolve the aliases and silently left those imports out.

### dependency-cruiser 18.7.2

Command: `npx --yes dependency-cruiser --no-config --ts-config $B/repos/vue-core/tsconfig.json --output-type json $B/repos/vue-core/packages`

| Run (npm cache already holds the tool) | Wall time (s) |
|---|---|
| 1 | 2.639387533 |
| 2 | 2.584619555 |
| 3 | 2.503171465 |

Result: 526 modules, 1887 dependencies, 477 modules that are resolved local files, 113 dependencies it could not resolve. The unresolved ones are external packages that are not installed (`@babel/types` 22, `vitest` 15, `@babel/parser` 11, `source-map-js` 8 and others) plus imports of build output that does not exist in a clean clone. It resolved 423 alias imports, 160 of them to `packages/shared/src/index.ts`.

## What was not measured

- **The dependency-cruiser first run including its npm download.** A mistake in my timing wrapper sent that number into the output file, which a later run overwrote. Only the three cached runs above exist.
- **Parallel parsing.** Everything is single-threaded on a 4-core machine.
- **A third "cold" level.** Cold here means the OS file cache was dropped. It does not cover a first-ever run on a freshly booted machine, and Python's own start-up is reported separately.
- **Incremental updates for commits that add, delete or rename modules, or that change many files.** Only the three latest commits (1 or 2 modified Python files each) were timed.
- **Dependents as of each commit.** Measurement 3 uses the HEAD graph for all 200 commits.
- **Transitive dependents.** Only direct importers were counted.
- **Dependents with tests excluded.** Test modules are counted as dependents throughout.
- **Rename-heavy diffs for `-M`.**
- **tree-sitter incremental re-parse with an edited old tree.**
- **Repositories larger than these.** The largest here is 2,943 modules or 814,376 lines of Python.
- **Any language other than Python and TypeScript, and any TypeScript repository other than vuejs/core.**
- **Run-to-run spread beyond three runs.** Each timing has three samples (the incremental and tree-sitter ones have three cold and three warm).
