import { test, expect } from "@playwright/test";

test.describe("Tennis App E2E Tests", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3000");
  });

  test("predicts match winner", async ({ page }) => {
    // Select players
    await page.selectOption("select >> nth=0", "Roger Federer");
    await page.selectOption("select >> nth=1", "Rafael Nadal");

    await expect(page.locator("text=/\\d+%/")).not.toBeVisible();

    // Click predict button and wait for response
    await page.click("text=Predict Winner");

    // Wait for percentage symbols to appear
    await expect(page.locator("text=/\\d+%/")).toHaveCount(2);

    // Verify probability elements are present and contain percentages
    const probabilityElements = await page.locator("text=/\\d+%/").all();
    expect(probabilityElements.length).toBe(2);
  });

  // Add retries for the LLM test
  test("chat interaction works", async ({ page }) => {
    test.slow(); // Increase timeouts for this test

    // Retry up to 3 times with increasing delays
    await test.step("LLM chat interaction", async () => {
      let success = false;
      for (let attempt = 0; attempt < 3 && !success; attempt++) {
        try {
          // Wait longer on subsequent attempts
          await page.waitForTimeout(attempt * 5000);

          // Find chat input and send message
          const chatInput = page.locator(
            'input[placeholder="Type your message..."]',
          );
          await chatInput.fill(
            "Who is more likely to win between Federer and Nadal on clay court? Just give me a name and a single reason.",
          );
          await page.click("text=Send");

          // Wait for and verify AI response with a longer timeout
          // we want to wait for a non-pending AI message
          const assistantResponse = await page
            .locator(
              '[data-testid="assistant-message"]:not([data-pending="true"])',
            )
            .first()
            .textContent({ timeout: 45_000 });
          expect(assistantResponse).toBeTruthy();

          // Verify both message types appear
          await expect(
            page.locator('[data-testid="user-message"]'),
          ).toHaveCount(1);
          await expect(
            page.locator('[data-testid="assistant-message"]'),
          ).toHaveCount(1);

          success = true;
        } catch (error) {
          console.log(error);
          if (attempt === 2) throw error; // Rethrow on last attempt
          console.log(`Attempt ${attempt + 1} failed, retrying...`);
        }
      }
    });
  });
});
