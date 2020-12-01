// Type definitions for additional types of Gviz

declare namespace google {
  namespace charts {
    function safeLoad(packages: object): void;
  }
  namespace visualization {
    namespace data {
      // tslint:disable-next-line:class-name
      export class group extends DataTable {
        // tslint:disable-next-line:no-any
        constructor(dataTable?: any, keys?: any, columns?: any);
      }
      function avg(): void;
      function count(): void;
      function max(): void;
      function min(): void;
      function sum(): void;
    }

    export interface ChartTooltip extends ChartTooltip {
      ignoreBounds?: boolean;
    }

    export interface DataTableCellFilter extends DataTableCellFilter {
      test?: (value: string) => boolean;
    }

    export class DataTableExt extends DataTable {
      getColumnIndex(column: number|string): number;
    }

    interface Intervals {
      style?: string;
      color?: string;
    }

    export interface LineChartOptions extends LineChartOptions {
      intervals?: Intervals;
    }
  }
}
