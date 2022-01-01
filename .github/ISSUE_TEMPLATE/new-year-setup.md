---
name: New year setup
about: Checklist for setting up a new year for the db/webapp.
title: 'New Year Setup: [YEAR]'
labels: new year
assignees: emilywritescode

---

[ ] **Create new table in database**
CREATE table albums\_[year] like [pick any of the other albums\_ tables];

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

*need to run server, and grab results from console*:
- [ ] first_listened_image (if needed, list separated by commas)
- [ ] last_listened_image (if needed, list separated by commas)
- [ ] total_time_ms

**UI side**
- [ ] albums.component: add table name to valid_stats_years
- [ ] insert-record.component: increase max release year

**Server side**
- [ ] config: 
  - [ ] add table name to valid_table_years
  - [ ] update latest_year