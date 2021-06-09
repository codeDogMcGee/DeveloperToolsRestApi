# DOE Developer Tools REST API


### API Endpoints
```
organizations/
```
Or to sort by column and direction use _organizations/<str:sort_column>/<int:ascending>/_., where acceptable values for
ascending are 1 for True, or 0 for False. For example:
```
organizations/total_labor_hours/0/
```
will return data sorted by total_labor_hours in descending order.