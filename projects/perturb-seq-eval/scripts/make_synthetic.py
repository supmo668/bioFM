"""Build the synthetic AnnData stub used by CI (no scanpy required)."""

from __future__ import annotations

from pathlib import Path

from perturb_eval.data import SyntheticPerturbSeq


def main() -> None:
    ds = SyntheticPerturbSeq()
    tr, va, te = ds.train(), ds.val(), ds.test()
    out = Path("data/synthetic.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as fh:
        for split in (tr, va, te):
            fh.write(
                f"{split.name}\tcells={split.n_cells}\tgenes={split.n_genes}\t"
                f"perturbations={','.join(split.perturbation_names)}\n"
            )
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
