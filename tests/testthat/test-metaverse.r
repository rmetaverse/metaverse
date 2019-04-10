context("test-metaverse.r")

test_that("Returns data.frame", {
  expect_is(metaverse_packages(include_self = TRUE), "character")
})
