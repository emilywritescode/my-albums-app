export class Record {

    constructor(
        public table: string,
        public album: string,
        public artist: string,
        public month: number,
        public day: number,
        public rel_year: string
    ) { }
}
