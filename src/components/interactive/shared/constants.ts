const RESET_VALUE = "__all__";

function resetValue(value: string): string {
  return value === RESET_VALUE ? "" : value;
}

export { RESET_VALUE, resetValue };
