// sleep the thread for ms miliseconds
export function sleeper(ms) {
  return function(x) {
    return new Promise(resolve => setTimeout(() => resolve(x), ms));
  };
}

export function doNothing() {
  return;
}

export function doNothingOnClick(e) {
  return;
}
