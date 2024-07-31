library(DBI)

conn <- dbConnect(RSQLite::SQLite(), 'bball_db') 
game_info <- dbReadTable(conn, "game_info")
game_info[game_info$Duration == 12360, 'Duration'] <- 126
dbWriteTable(conn, 'game_info', game_info, overwrite = T)
