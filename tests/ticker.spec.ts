import { test, expect } from '@playwright/test';

test('Página de detalhe de ticker carrega corretamente', async ({ page }) => {
  const response = await page.goto('/ticker/PETR4');
  expect(response?.ok()).toBeTruthy();

  await expect(page).toHaveURL(/\/ticker\/PETR4/);
  await expect(page.locator('h1')).toHaveText(/PETR4/);
  await expect(page.getByText('Preço Atual')).toBeVisible();
  await expect(page.getByText('Preço Justo (Graham)', { exact: false })).toBeVisible();
});
