# Basketball Data Analysis

This is a personal project to perform various analyses on basketball data,
mostly focused on making better decisions when playing fantasy basketball. This
requires data that can be webscraped using
[this project](https://github.com/Sonofacar/basketball-webscraper).

Below is an explanation of the various analyses currently in this repository:

## Minutes Modeling

As it sounds, I am attempting to project the amount of minutes (or really
seconds) a player will play in the upcoming season. The eventual goal is to use
these projections in conjunction with projections of their fantasy points to
grade players in a hypothetical fantasy draft.

## Multi-state Modeling

This is an attempt to model a player's health state as a multi-state model. The
main goal here is to find the force of transition for individual players to be
able to calculate an expected value of the player in similar ways to how the
actuaries might calculate the expected present value of a life insurance
policy. For the time being, this effort has mostly stalled out.
