# Country packs

`artemis offer` turns an offer into net pay and checks the contract against local employment law.
It reads `data/countries/<CODE>.md`, where `<CODE>` is the ISO country code in
`knowledge.json` → `candidate.country_pack`. If there's no pack for a country, Artemis researches the
rules, cites the sources, and says that an accountant should confirm.

Packs so far: `RO` (Romania).

## Add a pack for your country

Copy `RO.md`, keep the same headings, and fill in:
1. Gross → net for an employment contract (contributions, income tax, a rule of thumb at senior pay)
2. Contractor alternatives and what a contractor gives up
3. Employment-law points that matter in an offer: probation, notice, non-compete, paid leave
4. Market-data sources for pay
5. "Last reviewed" date and the legal sources

Then open a pull request. Packs are guidance, not tax or legal advice.
