interface MobileSortColumn<K extends string> {
  key: K;
  label: string;
}

interface MobileSortProps<K extends string> {
  columns: MobileSortColumn<K>[];
  sortKey: K;
  sortDirection: "asc" | "desc";
  toggleSort: (key: K) => void;
  styles: Record<string, string>;
}

function MobileSort<K extends string>({ columns, sortKey, sortDirection, toggleSort, styles }: MobileSortProps<K>) {
  return (
    <div className={styles.mobileSort}>
      <label className={styles.mobileSortLabel} htmlFor="mobile-sort">Sort</label>
      <select
        id="mobile-sort"
        className={styles.mobileSortSelect}
        value={sortKey}
        onChange={(e) => toggleSort(e.target.value as K)}
      >
        {columns.map((col) => (
          <option key={col.key} value={col.key}>{col.label}</option>
        ))}
      </select>
      <button
        type="button"
        className={styles.mobileSortDirection}
        onClick={() => toggleSort(sortKey)}
        aria-label={`Sort ${sortDirection === "asc" ? "ascending" : "descending"}`}
      >
        {sortDirection === "asc" ? "\u2191" : "\u2193"}
      </button>
    </div>
  );
}

export { MobileSort };
