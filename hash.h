#ifndef HASH_H
#define HASH_H

#include "reversi.h"

struct slot{
	board brd;
	calc_type alpha, beta;
	short height;
	pos_type pos;
};

class tank{
protected:
	static const int size = 15084637;
	slot* table;

public:
	tank(){
		table = new slot[size];
	}
	tank(const tank& tnk){
		table = new slot[size];
		memcpy(table, tnk.table,sizeof(slot) * size);
	}
	tank(tank&& tnk){
		table = tnk.table;
		tnk.table = NULL;
	}
	~tank(){
		delete table;
	}
	tank& operator=(const tank& tnk){
		memcpy(table, tnk.table,sizeof(slot) * size);
		return *this;
	}
	tank& operator=(tank&& tnk){
		delete table;
		table = tnk.table;
		tnk.table = NULL;
		return *this;
	}

	size_t mapping(const board& brd){
		return (
			brd.brd_black * 3727042349078977
			+ brd.brd_white * 9109418502615479
		) % size;
	}
	void clear(){
		for(int i = 0;i != size;++i){
			slot& slt = table[i];
			slt.height = 0;
			slt.alpha = _inf;
			slt.beta = inf;
		}
	}
	void insert(const slot& slt){
		table[mapping(slt.brd)] = slt;
	}
	slot& find(const board& brd){
		return table[mapping(brd)];
	}
};

#endif //HASH_H