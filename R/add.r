#' Add model values to a table of meta-analysis results
#'
#' Kyle, you got this and the rest of the tidymeta stuff from Malcome
#' DO NOT FORGET TO CREDIT HIM. Malcom if you're reading this I only did
#' it as a dirty hack to get your awesome work to work.
#'
#' `add_weights()` adds study weights to the model. `add_residuals()` and
#' `add_rstandard()` add residuals. `add_i2()`, `add_h2()`, `add_tau2()`
#'
#' @param x a tidied meta-analysis
#' @param .meta a meta-analysis object. If not `NULL`, then looks for a `meta`
#'   column in `x` containing an overall meta-analysis
#' @param group a grouping variable
#' @param exponentiate logical. Should the results be exponentiated?
#'
#' @return a `tbl`
#' @export
#'
#' @examples
#'
#' library(dplyr)
#'
#' iud_cxca %>%
#'   group_by(group) %>%
#'   meta_analysis(, yi = lnes, sei = selnes, slab = study_name) %>%
#'   add_i2()
#'
#' @rdname add
#' @name add
#'
#' @importFrom rlang !!
add_weights <- function(x, .meta = NULL, group = NULL) {
  .group <- rlang::enquo(group)
  wts <- pull_meta(x) %>%
    weights() %>%
    tibble::enframe("study", "weight")
  attributes(wts$study) <- NULL
  x <- dplyr::left_join(x, wts, by = "study")


  if (!rlang::quo_is_null(.group)) {
    x <- x %>%
      dplyr::group_by(!!.group) %>%
      dplyr::mutate(weight = ifelse(type == "summary",
                                    sum(weight, na.rm = TRUE), weight)) %>%
      dplyr::ungroup()
  }

  x %>%
    dplyr::mutate(weight = ifelse(study == "Overall", 100.00, weight))

}

#' @export
#' @rdname add
add_residuals <- function(x, .meta = NULL) {
  pull_meta(x) %>%
    residuals() %>%
    tibble::enframe("study", ".resid") %>%
    dplyr::left_join(x, ., by = "study")
}

#' @export
#' @rdname add
add_rstandard <- function(x, .meta = NULL) {
  pull_meta(x) %>%
    rstandard() %>%
    as.data.frame() %>%
    tibble::rownames_to_column("study") %>%
    dplyr::select(study, .std.resid = resid) %>%
    dplyr::left_join(x, ., by = "study")
}

#' @export
#' @rdname add
add_i2 <- function(x, .meta = NULL) {
  x %>% dplyr::mutate(i.squared = purrr::map_dbl(meta, function(.x) {
    if (is.null(.x)) NA_real_ else .x$I2
  }))
}

#' @export
#' @rdname add
add_h2 <- function(x, .meta = NULL) {
  x %>% dplyr::mutate(h.squared = purrr::map_dbl(meta, function(.x) {
    if (is.null(.x)) NA_real_ else .x$H2
  }))
}

#' @export
#' @rdname add
add_tau2 <- function(x, .meta = NULL) {
  x %>% dplyr::mutate(tau.squared = purrr::map_dbl(meta, function(.x) {
    if (is.null(.x)) NA_real_ else .x$tau2
  }))
}

#' #' @export
#' #' @rdname add
#' add_predictions <- function(x, .meta = NULL) {
#'  pull_meta(x) %>%
#'     predict() %>%
#'     tibble::enframe("study", "weight") %>%
#'     dplyr::left_join(x, ., by = "study")
#' }

#' @export
#' @rdname add
add_blups <- function(x, .meta = NULL, exponentiate = FALSE) {
  x <- pull_meta(x) %>%
    metafor::blup() %>%
    as.data.frame() %>%
    tibble::rownames_to_column("study") %>%
    dplyr::select(study, .fitted = pred, .se.fit = se,
                  .pil.fit = pi.lb, .piu.fit = pi.ub) %>%
    dplyr::left_join(x, ., by = "study")

  if (exponentiate) {
    x <- dplyr::mutate(.fitted = exp(.fitted),
                       .pil.fit = exp(.pil.fit),
                       .piu.fit = exp(.piu.fit))
  }

  x
}
