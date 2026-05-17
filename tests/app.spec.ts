import { test, expect } from '@playwright/test';

test('Página inicial carrega o dashboard', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Terminal Radar/);
  await expect(page.getByText('Market Watchlist')).toBeVisible();
  await expect(page.getByRole('button', { name: /Iniciar Scanner/i })).toBeVisible();
});

test('Página de watchlist carrega e exibe carteira', async ({ page }) => {
  await page.goto('/watchlist');
  await expect(page.getByText('Patrimônio Atualizado')).toBeVisible();
  await expect(page.getByRole('button', { name: /NOVA OPERAÇÃO/i })).toBeVisible();
});
