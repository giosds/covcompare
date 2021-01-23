# cov_compare

SHOWS DATA ON COVID IN ITALY BY AREA

Users select one or more Italian regions to see how they are affected by the pandemic.
This application provides in no way any scientific analysis on the pandemic: it just aims to be a visualization tool and a small personal project.

The raw new-cases data are smoothed, normalized (by population size) and a log transformation is applied. 
No assumptions or corrections are made on the data. Keep in mind the data have serious accuracy issues, due to the evolving situation in testing capabilities.

This is how to read the graph:
- The higher the slope, the faster the spread of the disease in the area
- It's a log: one more unit in the Y axis represents a multiplication in new cases by 'e' times
- The plot represents a transformation of the (new cases/population) ratio in each region. Thus when two lines cross, they have the same ratio.

Data sources:
- http://dati.istat.it/
- https://github.com/pcm-dpc/COVID-19
