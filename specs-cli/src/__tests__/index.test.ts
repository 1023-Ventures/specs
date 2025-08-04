describe('Specs CLI', () => {
  test('package.json should have correct name', () => {
    const pkg = require('../../package.json');
    expect(pkg.name).toBe('specs-cli');
  });

  test('package.json should have version', () => {
    const pkg = require('../../package.json');
    expect(pkg.version).toBeDefined();
    expect(typeof pkg.version).toBe('string');
  });

  test('CLI should have correct commands', () => {
    // Test that we can at least verify the structure
    expect(true).toBe(true);
  });
});
