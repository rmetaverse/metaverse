.onAttach <- function(...) {
  needed <- metaverse_pkgs[!is_attached(metaverse_pkgs)]
  if (length(needed) == 0)
    return()

  crayon::num_colors(TRUE)
  metaverse_attach()
}

is_attached <- function(x) {
  paste0("package:", x) %in% search()
}