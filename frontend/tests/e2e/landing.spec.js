import { test, expect } from "@playwright/test";

test("landing page renders its main sections", async ({ page }) => {
  await page.goto("http://127.0.0.1:3000/");

  await expect(page.locator(".hero-header")).toBeVisible();
  await expect(page.locator("#mission")).toBeVisible();
  await expect(page.locator("#features")).toBeVisible();
  await expect(page.locator("#benefits")).toBeVisible();

  await expect(page.locator(".benefit-trigger")).toHaveCount(3);
});

test("benefits accordion opens the selected panel", async ({ page }) => {
  await page.goto("http://127.0.0.1:3000/");

  const triggers = page.locator(".benefit-trigger");

  await expect(triggers.nth(0)).toHaveAttribute("aria-expanded", "true");

  await triggers.nth(1).click();

  await expect(triggers.nth(1)).toHaveAttribute("aria-expanded", "true");
  await expect(page.locator("#benefit-panel-1")).toBeVisible();
  await expect(triggers.nth(0)).toHaveAttribute("aria-expanded", "false");
});

test("mobile navigation works without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("http://127.0.0.1:3000/");

  await page.locator(".menu-toggle").click();

  await expect(page.locator("#mobile-menu")).toBeVisible();

  const hasOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth + 1
  );

  expect(hasOverflow).toBe(false);
});