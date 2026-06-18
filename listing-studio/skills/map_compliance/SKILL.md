---
name: map-compliance
description: Validate a proposed price against the supplier MAP floor and gross-margin rules. Use when pricing or compliance checking is required.
---

# MAP Compliance Skill

A pricing analyst uses this skill to verify that a proposed listing price:

1. **Does not undercut the MAP floor.** Suppliers set a minimum advertised
   price; breaching it voids the supply agreement and exposes Stockwell to
   chargebacks.

2. **Meets the margin floor.** Stockwell requires at least 20 % gross margin
   on every listing. Listing below cost, even above MAP, is not permitted.

## How to use this skill

Call the bundled `check_map.py` script with the SKU and proposed price:

```
python check_map.py NV-ALDSWORTH-DM 41900
```

The script exits 0 and prints a JSON result on success, or exits 1 with a
structured error message on failure. Use the JSON result to decide whether
to accept, adjust, or escalate the price.

## Bundled files

| File           | Purpose                                              |
|----------------|------------------------------------------------------|
| `check_map.py` | Validates a proposed price against MAP + margin rules |

## Security note

This skill executes `check_map.py` as a subprocess. Scope what the script
can touch: it reads only the pricing-rules data you provide; it writes
nothing. Review any update to this skill before deploying — a malicious
`check_map.py` could exfiltrate data or take a privileged action.
