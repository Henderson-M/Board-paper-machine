Hi Henry,

One-off catch-up run from your machine on Monday 19 October 2026, prompted by Caitlin's report that the machine was not reading RJAH or ROH papers. No sweep was run. One pack was analysed on Fable: Robert Jones and Agnes Hunt (RL1), board of 7 October 2026, 3 LEAD / 7 WORTH WATCHING / 3 FOI. This run sends 1 papers alert (Caitlin) and this report.

## What was wrong

- RJAH (RL1): the trust uploaded its 7 October pack on Monday 12 October, five days after the meeting. The 8 October run correctly found nothing; by 12 October the meeting was outside the 2-day lookback, so the 12 and 18 October runs never looked again. RJAH had also never had a papers page on its org record until 5 October, so its May and July packs were never seen either. No RJAH pack had ever been analysed.
- ROH (RRJ): publishes no forward schedule, so it has never had a date alert. Its June and July 2026 meeting books were detected on the watchlist and Caitlin got two "date unknown, please confirm" emails, but the skill had no step that analysed a watchlist pack afterwards, and the June alert wrongly called the 26MB pack too large to open. Nothing newer than the July book is on the ROH site as of today (checked live via Playwright); the July book gives the next meeting as 9 September 2026 and no September pack has been published six weeks on.

## Fixes shipped in this commit

- Step 7 detection window now reaches back 21 days (was 2), so a late-published pack is still caught. A meeting leaves the window once analysed, so the extra cost is one page read per unanalysed passed meeting per run.
- Step 7b watchlist packs are now dated by reading the document (fetch_pdf_text.py --head), accepted when the date is in the future or within the last 21 days, and sent to the analyser like any other pack. A DATE-UNKNOWN alert is now only for a document with no readable date, and even then the pack is analysed and the summary included.
- Step 10 wording for packs whose meeting has already happened.

## Still open

- Caitlin's other three date-alerted meetings in the last 60 days with no pack attached were not checked today: Wye Valley 3 Sep, UHNM 16 Sep, UHB 24 Sep.
- Across all correspondents, 52 of 267 non-retracted meetings in the last 60 days have no pack attached. The next full sweep will pick up any of those within 21 days under the new window; older ones will not be revisited.

— Board paper machine
