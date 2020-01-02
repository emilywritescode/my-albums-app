import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { YearlyStatsComponent } from './yearly-stats.component';

describe('YearlyStatsComponent', () => {
  let component: YearlyStatsComponent;
  let fixture: ComponentFixture<YearlyStatsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ YearlyStatsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(YearlyStatsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
