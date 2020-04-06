import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { InsertRecordComponent } from './insert-record.component';

describe('InsertRecordComponent', () => {
  let component: InsertRecordComponent;
  let fixture: ComponentFixture<InsertRecordComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ InsertRecordComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(InsertRecordComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
