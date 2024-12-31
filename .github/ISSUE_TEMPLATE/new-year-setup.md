---
name: New year setup
about: Checklist for setting up a new year for the db/webapp.
title: 'New Year Setup: [YEAR]'
labels: new year
assignees: emilywritescode

---

**Create new table in database**
- [ ] CREATE table albums\_[year] like [pick any of the other albums\_ tables];

**Create row in stats table, set initial data**
*can be found manually by looking at year's table*:
- [ ] table_year
- [ ] first_listened_album (if needed, list separated by commas)
- [ ] first_listened_artist (if needed, list separated by commas)
- [ ] first_listened_month
- [ ] first_listened_day
- [ ] last_listened_album (if needed, list separated by commas)
- [ ] last_listened_artist (if needed, list separated by commas)
- [ ] last_listened_month
- [ ] last_listened_day
- [ ] top_artist (if needed, list separated by commas)
- [ ] top_num
- [ ] num_albums

*FIRST, do the upgrade steps below... THEN navigate to stats page for the desired year, and grab result for the total time listened from terminal window console. The check for the total time listened is first, so that value needs to be in the DB before the server returns the cover images. Refresh the stats page, and grab the cover image links from the terminal window console, and update the DB again. Refresh one last time for the stats page to load!*
- [ ] total_time_ms
- [ ] first_listened_image (if needed, list separated by commas)
- [ ] last_listened_image (if needed, list separated by commas)


**UI side**
- [ ] albums.component.ts: add table name to valid_stats_years
- [ ] insert-record.component.html: increase max release year

**Server side**
- [ ] config: 
  - [ ] add table name to valid_table_years
  - [ ] update latest_year
