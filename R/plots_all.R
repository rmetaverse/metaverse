#' Quickly plot common visualizations for meta-analyses
#'
#' `forest_plot()` presents study and summary estimates. `influence_plot()`
#' shows the forest plot of senstivity analyses using `senstivity()`.
#' `cumulative_plot()` shows the forest plot for `cumulative()`. `funnel_plot()`
#' plots standard errors against the summary esitimate to assess publication
#' bias.
#'
#' These were all taken from Malcolm Barrett, Kyle whatever you do NOT forget to
#' have Charles talk to him and make sure he is credited 100% for this.
#'
#' @param x a tidied meta-analysis
#' @param ... additional arguments
#' @param estimate variable name of point estimates
#' @param study variable name of study labels
#' @param size point size; either an aesthetic variable or a specific shape.
#' @param shape shape of the points; either an aesthetic variable or a specific
#'   shape.
#' @param col color of the points and lines; either an aesthetic variable or a
#'   specific color.
#' @param xmin lower confidence interval variable name
#' @param xmax upper confidence interval variable name
#' @param group a grouping variable
#' @param alpha transparancy level
#' @param height line height for error bars
#' @param std.error variable name of standard error variable
#' @param reverse_y logical. Should the y-axis be reversed?
#' @param log_summary logical. Should the estimate and confidence intervals be
#'   log-transformed?
#' @param sum_lines logical. Should vertical lines demarcating the summary
#'   estimate and confidence intervals be included?
#'
#' @return a `ggplot2` object
#' @export forest_plot
#'
#' @examples
#'
#' library(dplyr)
#'
#' ma <- iud_cxca %>%
#'   group_by(group) %>%
#'   meta_analysis(yi = lnes, sei = selnes, slab = study_name)
#'
#' forest_plot(ma)
#'
#' funnel_plot(ma)
#'
#' ma %>%
#'   sensitivity() %>%
#'   influence_plot()
#'
#' ma %>%
#'   cumulative() %>%
#'   cumulative_plot()
#'
#' @rdname quickplots
#'
#' @importFrom rlang !!
forest_plot <- function(x, estimate = estimate, study = study, size = weight,
                        shape = type, col = type, xmin = conf.low,
                        xmax = conf.high, group = NULL, alpha = .75, height = 0,
                        ...) {

  .estimate <- rlang::enquo(estimate)
  .study <- rlang::enquo(study)
  .studycol <- rlang::quo_text(.study)
  .size <- rlang::enquo(size)
  .shape <- rlang::enquo(shape)
  .col <- rlang::enquo(col)
  .group <- rlang::enquo(group)
  .groupcol <- rlang::quo_text(.group)
  .xmin <- rlang::enquo(xmin)
  .xmax <- rlang::enquo(xmax)

  if (is.null(x$weight)) {

  }

  x <- x %>%
    dplyr::mutate(!!.studycol := lock_order(!!.study))

  if (!rlang::quo_is_null(.group)) {
    x <- x %>%
      dplyr::mutate(!!.groupcol := lock_order(!!.group, rev = FALSE))
  }

  p <- x %>%
    ggplot2::ggplot(ggplot2::aes(x = !!.estimate, y = !!.study,
                                 shape = !!.shape, col = !!.col)) +
    ggplot2::geom_point(ggplot2::aes(size = !!.size), alpha = alpha) +
    theme_forest()

  if (!rlang::quo_is_null(.xmin)) {
    p <- p + ggplot2::geom_errorbarh(ggplot2::aes(xmin = !!.xmin,
                                                  xmax = !!.xmax),
                                     height = height,
                                     alpha = alpha)
  }

  if (!rlang::quo_is_null(.group)) {
    p <- p + ggplot2::facet_grid(ggplot2::vars(!!.group), scales = "free",
                                 space = "free", switch = "y")
  }
  p
}

#' @rdname quickplots
#' @export
#' @importFrom rlang !!
influence_plot <- function(x, estimate = l1o_estimate, study = study, size = 4,
                           shape = 15, col = type, xmin = l1o_conf.low,
                           xmax = l1o_conf.high, group = NULL, alpha = .75, height = 0,
                           sum_lines = TRUE, ...) {

  .estimate <- rlang::enquo(estimate)
  .study <- rlang::enquo(study)
  .col <- rlang::enquo(col)
  .studycol <- rlang::quo_text(.study)
  .group <- rlang::enquo(group)
  .groupcol <- rlang::quo_text(.group)
  .xmin <- rlang::enquo(xmin)
  .xmax <- rlang::enquo(xmax)


  vline_data <- data.frame(cuts = pull_summary(x, conf.int = TRUE),
                           type = c("Estimate", "95% CI", "95% CI"))
  x <- x %>%
    dplyr::filter(!stringr::str_detect(study, "Subgroup")) %>%
    dplyr::mutate(!!.studycol := lock_order(!!.study))

  if (!rlang::quo_is_null(.group)) {
    x <- x %>%
      dplyr::mutate(!!.groupcol := lock_order(!!.group, rev = FALSE))
  }



  p <- x %>%
    dplyr::mutate(estimate = !!.estimate, !!.studycol := lock_order(!!.study)) %>%
    ggplot2::ggplot(ggplot2::aes(x = estimate, y = !!.study, col = forcats::fct_rev(!!.col))) +
    ggplot2::geom_point(shape = shape, size = size, alpha = alpha) +
    theme_forest()

  if (sum_lines) p <- p + ggplot2::geom_vline(data = vline_data,
                                              ggplot2::aes(xintercept = cuts,
                                                           linetype = type))

  if (!rlang::quo_is_null(.xmin)) {
    p <- p + ggplot2::geom_errorbarh(ggplot2::aes(xmin = !!.xmin,
                                                  xmax = !!.xmax),
                                     height = height,
                                     alpha = alpha)
  }

  if (!rlang::quo_is_null(.group)) {
    p <- p + ggplot2::facet_grid(ggplot2::vars(!!.group), scales = "free",
                                 space = "free", switch = "y")
  }
  p
}


#' @rdname quickplots
#' @export
#' @importFrom rlang !!
cumulative_plot <- function(x, estimate = cumul_estimate, study = study, size = 4,
                            shape = 15, col = type, xmin = cumul_conf.low,
                            xmax = cumul_conf.high, group = NULL, alpha = .75, height = 0,
                            sum_lines = TRUE, ...) {
  .estimate <- rlang::enquo(estimate)
  .study <- rlang::enquo(study)
  .col <- rlang::enquo(col)
  .group <- rlang::enquo(group)
  .xmin <- rlang::enquo(xmin)
  .xmax <- rlang::enquo(xmax)

  influence_plot(x = x, estimate = !!.estimate, study = !!.study, size = size,
                 shape = shape, col = !!.col, xmin = !!.xmin,
                 xmax = !!.xmax, group = !!.group, alpha = alpha, height = height,
                 sum_lines = sum_lines, ...)
}


#' @rdname quickplots
#' @export
#' @importFrom rlang !!
funnel_plot <- function(x, estimate = estimate, std.error = std.error, size = 3,
                        shape = NULL, col = NULL, alpha = .75, reverse_y = TRUE,
                        log_summary = FALSE, ...) {

  .estimate <- rlang::enquo(estimate)
  .std.error <- rlang::enquo(std.error)
  .shape <- rlang::enquo(shape)
  .col <- rlang::enquo(col)

  mapping <- ggplot2::aes(x = !!.estimate, y = !!.std.error,
                          col = !!.col, shape = !!.shape)

  if (rlang::quo_is_null(.col)) mapping$colour <- NULL
  if (rlang::quo_is_null(.shape)) mapping$shape <- NULL


  p <- x %>%
    dplyr::filter(type == "study") %>%
    ggplot2::ggplot(mapping) +
    ggplot2::geom_point(size = size) +
    geom_funnel(ggplot2::aes(summary = pull_summary(x)),
                log_summary = log_summary) +
    theme_meta() +
    ggplot2::theme(legend.position = "right") +
    ggplot2::scale_linetype_discrete(name = "")

  if (log_summary) p <- p + scale_x_log()
  if (reverse_y) p <- p + ggplot2::scale_y_reverse()

  p
}

#' Lock the order of the data in the plot
#'
#' `lock_order()` locks the order of the of an axis variable exactly as it
#' appears in the data, rather than from the bottom up (for factors and
#' numerics) or in alphabetical order (for characters).
#'
#' @param var a variable to lock
#' @param rev logical. Should the order be reversed to make it appear on the
#'   plot as in the data? Default is `TRUE`.
#'
#' @return a factor
#' @export
#'
#' @examples
#'
#' library(ggplot2)
#'
#' meta_analysis(iud_cxca, yi = lnes, sei = selnes, slab = study_name) %>%
#'   ggplot(aes(x = estimate, y = lock_order(study))) +
#'   geom_point()
lock_order  <- function(var, rev = TRUE) {
  var <- forcats::fct_inorder(var)
  if (rev) var <- forcats::fct_rev(var)
  var
}

#' Group summary estimates together
#'
#' The default in `tidymeta` is to put subgroup estimates in the same group as
#' the estimates; `sub2summary()` gives them a value of "Overall", which groups
#' all summaries together.
#'
#' @param x a tidied meta-analysis
#' @param group a grouping variable
#' @param ... additional arguments
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
#'   meta_analysis(yi = lnes, sei = selnes, slab = study_name) %>%
#'   sub2summary(group)
#'
#' @importFrom rlang !!
sub2summary <- function(x, group, ...) {
  .group <- rlang::enquo(group)
  .groupcol <- rlang::quo_text(.group)
  x %>%
    dplyr::mutate(!!.groupcol := ifelse(stringr::str_detect(study, "Subgroup"),
                                        "Summary",
                                        !!.group)) %>%
    dplyr::arrange(type)
}
