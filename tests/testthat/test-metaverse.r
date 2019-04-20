context("test-metaverse.r")

test_that("Starts the metaverse package", {
  expect_is(metaverse_packages(include_self = TRUE), "character")
  expect_is(metaverse_packages(include_self = FALSE), "character")
})

test_that("Number of attached packages", {
  expect_length(metaverse_packages(include_self = TRUE), 13)
  expect_length(metaverse_packages(include_self = FALSE), 12)
})
